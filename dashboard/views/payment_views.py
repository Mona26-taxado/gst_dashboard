from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Equipment, EquipmentOrder
from decimal import Decimal

@login_required
def billing_details(request, equipment_id):
    try:
        equipment = Equipment.objects.get(id=equipment_id)
        
        # Calculate GST and total amount
        gst_amount = float(equipment.price) * 0.18
        total_amount = float(equipment.price) + gst_amount
        
        context = {
            'equipment': equipment,
            'gst_amount': "{:.2f}".format(gst_amount),
            'total_amount': "{:.2f}".format(total_amount)
        }
        
        if request.method == 'POST':
            # Create new order
            order = EquipmentOrder.objects.create(
                equipment=equipment,
                user=request.user,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                pincode=request.POST.get('pincode'),
                base_price=Decimal(str(equipment.price)),
                gst_amount=Decimal(str(gst_amount)),
                total_amount=Decimal(str(total_amount))
            )
            
            # Store order ID in session
            request.session['current_order_id'] = order.id
            
            # Redirect to payment processing
            return redirect('process_payment')
            
        return render(request, 'equipment_store/equipment_billing_details.html', context)
        
    except Equipment.DoesNotExist:
        messages.error(request, 'Equipment not found.')
        return redirect('equipment_store')

@login_required
def process_payment(request):
    # Get current order from session
    order_id = request.session.get('current_order_id')
    if not order_id:
        messages.error(request, 'No active order found.')
        return redirect('equipment_store')
    
    order = get_object_or_404(EquipmentOrder, id=order_id)
    equipment = order.equipment
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('process_payment')
            
        # Here you would integrate with your payment gateway
        # For now, we'll simulate a successful payment
        order.payment_status = 'PAID'
        order.payment_date = timezone.now()
        order.save()
        
        # Reduce equipment stock
        equipment.stock -= 1
        equipment.save()
        
        # Clear session
        if 'current_order_id' in request.session:
            del request.session['current_order_id']
            
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('equipment_store')
    
    context = {
        'equipment': equipment,
        'order': order
    }
    
    return render(request, 'equipment_store/payment_processing.html', context) 