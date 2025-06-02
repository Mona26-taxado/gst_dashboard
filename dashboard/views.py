import qrcode
import base64
from io import BytesIO
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Equipment, EquipmentOrder, Service
from django.db.models import Count, Sum


@login_required
def equipment_billing(request, equipment_id):
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
    if request.method == 'POST':
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
            quantity=quantity,
            status='pending'
        )
        
        # Generate UPI payment link
        upi_id = "9336323478@okbizaxis"
        upi_link = f"upi://pay?pa={upi_id}&pn=Grahak%20Sahaayata%20Kendra&am={total_amount}&tn=Order%20{order.id}"
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_link)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 string
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'order_id': order.id,
            'total_amount': total_amount,
            'qr_code': qr_code_base64,
        }
        
        return render(request, 'equipment_store/payment.html', context)
    
    return redirect('equipment_store')

@login_required
def check_payment_status(request, order_id):
    order = get_object_or_404(EquipmentOrder, id=order_id)
    # In a real application, you would implement actual payment verification here
    # For now, we'll just return a dummy response
    return JsonResponse({
        'status': 'pending',
        'message': 'Payment verification in progress'
    })

@login_required
def retailer_dashboard(request):
    if not request.user.is_retailer:
        return redirect('home')
    return render(request, 'retailer_dashboard/retailer_dashboard.html')

@login_required
def get_retailer_services_distribution(request):
    if not request.user.is_retailer:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Get all services for the retailer
        services = Service.objects.filter(retailer=request.user.retailer)
        
        # Group services by type and count them
        service_counts = services.values('service_type').annotate(count=Count('id'))
        service_amounts = services.values('service_type').annotate(total=Sum('amount'))
        
        # Prepare data for the chart
        labels = []
        data = []
        total_services = 0
        total_billing = 0
        
        for service in service_counts:
            labels.append(service['service_type'])
            data.append(service['count'])
            total_services += service['count']
        
        for amount in service_amounts:
            total_billing += float(amount['total'])
        
        return JsonResponse({
            'labels': labels,
            'data': data,
            'total_services': total_services,
            'total_billing': total_billing
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
