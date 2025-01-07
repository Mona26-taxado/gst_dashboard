from django.shortcuts import render, redirect, get_object_or_404
from dashboard.utils import role_required, generate_qr
from django.contrib.auth.decorators import login_required
from dashboard.models import Notification
from dashboard.models import Customer, CustomUser
from django.contrib import messages
from dashboard.models import Service, BillingDetails,Transaction, Wallet, Transaction
from dashboard.forms import AddCustomerForm, BillingDetailsForm
from datetime import date
import random
from django.http import JsonResponse
from decimal import Decimal
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Sum
from django.http import HttpResponseForbidden, HttpResponse
from dashboard.models import CustomUser
import qrcode
from django.http import Http404
import logging
import os
from dashboard.models import BankingPortalAccessRequest






@login_required
def retailer_dashboard(request):
    # Your logic for the retailer dashboard
    return render(request, 'retailer_dashboard/retailer_dashboard.html')


def pin_entry(request):
    """
    View for managing PIN entry.
    """
    return render(request, 'pin_entry.html')









@role_required(['retailer'])
def retailer_dashboard(request):
    # Fetch notifications for the current user
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0.0
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Count total services
    total_services = Service.objects.filter(status='active').count()  # Assuming active status filtering
    
    # Count total billings for the retailer
    total_billings = BillingDetails.objects.filter(user=request.user).count()
    
    # Pass total_services to the context
    context = {
        'notifications': notifications,
        'total_services': total_services,
        'wallet_balance': wallet_balance,
        'total_billings': total_billings,  # Include total billings count
    }
    return render(request, 'retailer_dashboard/retailer_dashboard.html', context)




@role_required(['retailer', 'distributor', 'master_distributor'])
def view_services(request):
    # Fetch only active services
    services = Service.objects.filter(status='active').values('service_name', 'price', 'status')
    paginator = Paginator(services, 7)  # Show 7 services per page

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the global serial number for the current page
    start_index = page_obj.start_index()

    # Debugging
    print("DEBUG: Retailer Services ->", list(services))

    context = {
        'services': services,
        'page_obj': page_obj,
        'start_index': start_index,
    }
    return render(request, 'retailer_dashboard/view_services.html', context)






# Add Customer
@role_required(['retailer'])
def add_customer(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
        if form.is_valid():
            # Do not save to database yet; instead, create an object
            customer = form.save(commit=False)
            # Set the `created_by` field to the logged-in user
            customer.created_by = request.user
            # Now save the object to the database
            customer.save()
            messages.success(request, "Customer added successfully!")
            return redirect('view_customer')  # Redirect after successful save
    else:
        form = AddCustomerForm()
    return render(request, 'retailer_dashboard/add_customer.html', {'form': form})






@role_required(['retailer'])
@login_required
def view_customer(request):
    # Ensure the logged-in user is a retailer
    if request.user.role != 'retailer':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch only the customers created by the logged-in retailer
    customers = Customer.objects.filter(created_by=request.user).order_by('id')

    # Pagination (7 customers per page)
    paginator = Paginator(customers, 7)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the global serial number for the current page
    start_index = page_obj.start_index()

    return render(request, 'retailer_dashboard/view_customer.html', {
        'page_obj': page_obj,
        'start_index': start_index,
    })




@role_required(['retailer'])  # Restrict access to specific roles
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        # Fetch updated data from the form
        customer.full_name = request.POST.get('full_name', customer.full_name)
        customer.gender = request.POST.get('gender', customer.gender)
        customer.dob = request.POST.get('dob', customer.dob)  # Ensure the date format is correct
        customer.address = request.POST.get('address', customer.address)
        customer.state = request.POST.get('state', customer.state)
        customer.city = request.POST.get('city', customer.city)
        customer.email = request.POST.get('email', customer.email)
        customer.mobile = request.POST.get('mobile', customer.mobile)
        
        # Save the changes
        dob = request.POST.get('dob')
        if dob:  # If dob is provided, validate it
            try:
                customer.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return render(request, 'retailer_dashboard/edit_customer.html', {'customer': customer})
        else:
            messages.error(request, "Date of birth cannot be empty.")
            return render(request, 'retailer_dashboard/edit_customer.html', {'customer': customer})
        customer.save()
        customer.save()

        messages.success(request, "Customer updated successfully!")
        return redirect('view_customer')  # Redirect after successful update

    return render(request, 'retailer_dashboard/edit_customer.html', {'customer': customer})





@role_required(['retailer'])
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('view_customer')  # Ensure the name matches the URL pattern in urls.py







def add_billing(request):
    if request.method == 'POST':
        # Fetch the logged-in user's wallet
        wallet = Wallet.objects.get(user=request.user)

        # Fetch the selected service
        service_id = request.POST.get('service')
        service = Service.objects.get(id=service_id)

        # Get the service price
        service_price = service.price

        # Check if the wallet has sufficient balance
        if wallet.balance < service_price:
            # Show an error message if balance is insufficient
            return JsonResponse({"error": "Insufficient balance to add billing for this service"}, status=400)

        # Deduct the service price from the wallet
        wallet.balance -= service_price
        wallet.save()

        # Log the transaction
        Transaction.objects.create(
            user=request.user,
            amount=service_price,
            transaction_type="Debit",
            balance_after_transaction=wallet.balance,
            description=f"Service Charge for {service.service_name}",
        )

        # Proceed with adding billing details
        customer_id = request.POST.get('customer')
        payment_mode = request.POST.get('payment_mode')
        payment_status = request.POST.get('payment_status')
        service_status = 'Pending'
        ref_no = f"REF-942-{random.randint(100000000, 999999999)}"
        id_proof = request.FILES.get('id_proof')
        address_proof = request.FILES.get('address_proof')
        photo = request.FILES.get('photo')

        # Fetch the customer object
        customer = Customer.objects.get(id=customer_id)

        # Create the BillingDetails object
        BillingDetails.objects.create(
            user=request.user,
            ref_no=ref_no,
            customer=customer,
            service=service,
            payment_mode=payment_mode,
            payment_status=payment_status,
            service_status=service_status,
            id_proof=id_proof,  # Save the uploaded file
            address_proof=address_proof,
            photo=photo,
        )

        return redirect('view_billing')

    # Render the form with necessary data
    customers = Customer.objects.all()
    services = Service.objects.filter(status='active')
    return render(request, 'retailer_dashboard/add_billing.html', {
        'customers': customers,
        'services': services,
    })








# View Billing Details
@role_required(['retailer'])
@login_required
def view_billing(request):
    # Ensure the logged-in user is a retailer
    if request.user.role != 'retailer':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch only the billing records created by the logged-in retailer
    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')

    # Pagination (e.g., 10 billing records per page)
    paginator = Paginator(billing_details, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'retailer_dashboard/view_billing.html', {
        'page_obj': page_obj,
    })








# View for editing billing details
# View Billing Details
def view_billing_details(request, billing_id):
    billing_details = get_object_or_404(BillingDetails, id=billing_id)
    customer = billing_details.customer  # Get the customer details
    retailer = request.user  # Assuming the logged-in user is the retailer
    
    context = {
        'billing_details': billing_details,
        'customer': customer,
        'retailer': retailer,
    }
    return render(request, 'retailer_dashboard/view_billing_details.html', context)






# Edit Billing Details
def edit_billing(request, billing_id):
    billing_details = get_object_or_404(BillingDetails, id=billing_id)

    # Fetch all active services for the dropdown
    services = Service.objects.filter(status="active")

    if request.method == 'POST':
        form = BillingDetailsForm(request.POST, request.FILES, instance=billing_details)
        if form.is_valid():
            # Update the service status dynamically based on admin inputs
            billing_details.id_proof = request.FILES.get('id_proof', billing_details.id_proof)
            billing_details.address_proof = request.FILES.get('address_proof', billing_details.address_proof)
            billing_details.photo = request.FILES.get('photo', billing_details.photo)
            billing_details.save()
            # Redirect to the retailer's View Billing page
            return redirect('retailer_view_billing')
    else:
        form = BillingDetailsForm(instance=billing_details)

    return render(
        request,
        'retailer_dashboard/edit_billing.html',
        {
            'form': form,
            'billing_details': billing_details,
            'services': services,  # For service dropdown
        },
    )



def view_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    return render(request, "retailer_dashboard/wallet.html", {"wallet": wallet})





@login_required
def retailer_view_transactions(request):
    if request.user.role != 'retailer':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch transactions for the logged-in retailer
    retailer = request.user
    transactions = Transaction.objects.filter(user=retailer).order_by('-created_at')

    # Add pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
    }

    return render(request, 'retailer_dashboard/view_transactions.html', context)





@role_required(['retailer'])
def generate_qr_for_recharge(request, user_id):
    try:
        retailer = CustomUser.objects.get(id=user_id)
        user_name = retailer.full_name

        # Generate the QR code
        qr_code_path = generate_qr(user_name)

        return render(request, 'retailer_dashboard/recharge_wallet.html', {
            'user_name': user_name,
            'qr_code': qr_code_path,
            'user_id': user_id,  # Pass user_id for the form action
        })
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")






@role_required(['retailer'])
def wallet_recharge_view(request):
    retailer = request.user  # Get the logged-in retailer
    user_name = retailer.full_name
    qr_code_path = os.path.join('static', 'qr_codes', f"{user_name.replace(' ', '_')}_qr.png")

    return render(request, 'retailer_dashboard/wallet_recharge.html', {
        'user_name': user_name,
        'qr_code': qr_code_path,
    })



@login_required
def banking_portal_request(request):
    # Check if the user already has an active request
    try:
        access_request = BankingPortalAccessRequest.objects.get(user=request.user)
        if access_request.is_active:
            return redirect('https://taxado.finstore.app/')  # Redirect to banking portal if already active
        else:
            messages.info(request, "Your request is pending. Please wait for approval.")
    except BankingPortalAccessRequest.DoesNotExist:
        # Create a new request if none exists
        if request.method == 'POST':
            BankingPortalAccessRequest.objects.create(user=request.user)
            messages.success(request, "Your request has been submitted successfully.")
            return redirect('request_access')  # Redirect to the dashboard after request submission

    return render(request, 'retailer_dashboard/request_access.html')