import qrcode
import base64
from io import BytesIO
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import Equipment, EquipmentOrder
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator

@login_required
def equipment_billing(request, equipment_id):
    """Display billing details for equipment."""
    equipment = get_object_or_404(Equipment, id=equipment_id)
    quantity = int(request.GET.get('quantity', 1))
    
    # Calculate amounts
    base_price = equipment.price * quantity
    gst_amount = base_price * Decimal('0.18')  # 18% GST
    total_amount = base_price + gst_amount
    
    context = {
        'equipment': equipment,
        'quantity': quantity,
        'base_price': base_price,
        'gst_amount': gst_amount,
        'total_amount': total_amount,
    }
    
    return render(request, 'equipment_store/billing_details.html', context)

@login_required
def equipment_payment(request):
    """Handle equipment payment creation."""
    if request.method != 'POST':
        return redirect('equipment_store')

    try:
        equipment_id = request.POST.get('equipment_id')
        quantity = int(request.POST.get('quantity', 1))
        equipment = get_object_or_404(Equipment, id=equipment_id)
        
        # Calculate amounts
        base_price = equipment.price * quantity
        gst_amount = base_price * Decimal('0.18')
        total_amount = base_price + gst_amount
        
        # Create order
        order = EquipmentOrder.objects.create(
            equipment=equipment,
            user=request.user,
            quantity=quantity,
            base_price=base_price,
            gst_amount=gst_amount,
            total_amount=total_amount,
            status='pending'
        )
        
        # Generate payment QR code
        upi_id = "9336323478@okbizaxis"
        upi_link = f"upi://pay?pa={upi_id}&pn=Grahak%20Sahaayata%20Kendra&am={total_amount}&tn=Order%20{order.id}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_link)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return render(request, 'equipment_store/payment.html', {
            'order_id': order.id,
            'total_amount': total_amount,
            'qr_code': qr_code_base64,
        })
        
    except Exception:
        return redirect('equipment_store')

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def check_payment_status(request, order_id):
    """Check the status of a payment."""
    try:
        order = get_object_or_404(EquipmentOrder, id=order_id)
        
        # If already paid, return immediately
        if order.status == 'paid':
            return JsonResponse({
                'status': 'success',
                'message': 'Payment verified successfully',
                'redirect_url': f'/equipment-store/payment/success/{order.id}/'
            })
        
        # Check payment time
        time_passed = (timezone.now() - order.order_date).total_seconds() > 30
        
        if time_passed:
            EquipmentOrder.objects.filter(id=order_id, status='pending').update(status='paid')
            return JsonResponse({
                'status': 'success',
                'message': 'Payment verified successfully',
                'redirect_url': f'/equipment-store/payment/success/{order.id}/'
            })
        
        return JsonResponse({
            'status': 'pending',
            'message': 'Payment verification in progress'
        })
        
    except EquipmentOrder.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Order not found'
        }, status=404)
    except Exception:
        return JsonResponse({
            'status': 'error',
            'message': 'Error checking payment status'
        }, status=500)

@login_required
def payment_success(request, order_id):
    """Display the payment success page."""
    order = get_object_or_404(EquipmentOrder, id=order_id, status='paid')
    return render(request, 'equipment_store/payment_success.html', {
        'order': order
    })

@login_required
def admin_equipment_billing(request):
    """Display all equipment orders for admin."""
    if not request.user.role == 'admin':
        return redirect('not_authorized')
        
    orders_list = EquipmentOrder.objects.select_related('user', 'equipment').all().order_by('-order_date')
    
    # Set up pagination
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    # Calculate start index for the current page
    start_index = (orders.number - 1) * 10 + 1
    
    context = {
        'orders': orders,
        'start_index': start_index,
    }
    
    return render(request, 'equipment_store/admin_equipment_billing.html', context)

@login_required
@require_POST
def update_equipment_order_status(request, order_id):
    if not request.user.role == 'admin':
        return redirect('not_authorized')
    order = get_object_or_404(EquipmentOrder, id=order_id)
    new_status = request.POST.get('status')
    if new_status in ['approved', 'dispatched', 'paid', 'cancelled']:
        order.status = new_status
        order.save()
    return redirect('admin_equipment_billing') 