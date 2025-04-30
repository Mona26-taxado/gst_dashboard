from django.shortcuts import render, redirect, get_object_or_404
from dashboard.utils import role_required, generate_qr
from django.utils import timezone
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
from django.db.models import Sum, Count
from django.db.models import  Q
from django.http import HttpResponseForbidden, HttpResponse
from dashboard.models import CustomUser
import qrcode
import uuid
from django.http import Http404
import logging
import os
from dashboard.models import BankingPortalAccessRequest
import calendar






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

    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')[:7]  # Sort by newest first
    
    # Pass total_services to the context
    context = {
        'notifications': notifications,
        'total_services': total_services,
        'wallet_balance': wallet_balance,
        'total_billings': total_billings,  # Include total billings count
        'billing_details': billing_details,  # Include billing details for the retailer
    }
    return render(request, 'retailer_dashboard/retailer_dashboard.html', context)




@role_required(['retailer', 'distributor', 'master_distributor'])
def view_services(request):
    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Filter services based on the search query and active status, and sort alphabetically (A to Z)
    if search_query:
        services = Service.objects.filter(service_name__icontains=search_query, status='active').order_by('service_name')
    else:
        services = Service.objects.filter(status='active').order_by('service_name')

    # Pagination
    paginator = Paginator(services, 10)  # Show 10 services per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the global serial number for the current page
    start_index = page_obj.start_index()

    context = {
        'services': page_obj,  # Pass only the paginated services
        'page_obj': page_obj,
        'start_index': start_index,
        'search_query': search_query,  # Pass the search query to retain it in the search bar
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
            return redirect('retailer_add_billing')  # Redirect after successful save
    else:
        form = AddCustomerForm()
    return render(request, 'retailer_dashboard/add_customer.html', {'form': form})






@role_required(['retailer'])
@login_required
def view_customer(request):
    # Ensure the logged-in user is a retailer
    if request.user.role != 'retailer':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Get the search query from the GET request
    search_query = request.GET.get('search', '')

    # Fetch only the customers created by the logged-in retailer and apply the search filter if a query exists
    customers = Customer.objects.filter(created_by=request.user)
    if search_query:
        customers = customers.filter(
            Q(full_name__icontains=search_query) |  # Search by customer name
            Q(email__icontains=search_query)  # Add other search fields as needed
        )

    # Order customers by newest first
    customers = customers.order_by('-created_at')

    # Pagination (10 customers per page)
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the global serial number for the current page
    start_index = page_obj.start_index()

    return render(request, 'retailer_dashboard/view_customer.html', {
        'page_obj': page_obj,
        'start_index': start_index,
        'search_query': search_query,  # Pass the search query to the template
    })






@role_required(['retailer'])  # Restrict access to specific roles
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        print("POST Data Received:", request.POST)  # Debug POST data

        # Fetch and update fields
        customer.full_name = request.POST.get('full_name', customer.full_name)
        customer.gender = request.POST.get('gender', customer.gender)
        customer.address = request.POST.get('address', customer.address)
        customer.state = request.POST.get('state', customer.state)
        customer.city = request.POST.get('city', customer.city)
        customer.email = request.POST.get('email', customer.email)
        customer.mobile = request.POST.get('mobile', customer.mobile)

        # Handle DOB validation
        dob = request.POST.get('dob')
        if dob:
            try:
                customer.dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return render(request, 'retailer_dashboard/edit_customer.html', {'customer': customer})
        else:
            customer.dob = None  # Allow clearing DOB if not provided

        # Save the updated customer
        print("Before Save:", customer)  # Debug before save
        customer.save()
        print("After Save:", customer)  # Debug after save

        messages.success(request, "Customer updated successfully!")
        return redirect('retailer_view_customer')  # Redirect after successful update

    # Render the edit form
    return render(request, 'retailer_dashboard/edit_customer.html', {'customer': customer})








@role_required(['retailer'])
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('retailer_view_customer')  # Ensure the name matches the URL pattern in urls.py






@role_required(['retailer'])
def add_billing(request):
    if request.method == 'POST':
        # Fetch the logged-in user's wallet
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found. Please contact support.")
            return redirect('retailer_dashboard')

        # Fetch the selected service
        service_id = request.POST.get('service')
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            messages.error(request, "Invalid service selected.")
            return redirect('add_billing')

        service_price = service.price

        # Check wallet balance
        if wallet.balance < service_price:
            messages.error(
                request,
                "Insufficient balance to add billing for this service. Please recharge your wallet."
            )
            return redirect('retailer_add_billing')

        # Deduct service price from the wallet
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

        # Create Billing Details
        customer_id = request.POST.get('customer')
        payment_mode = request.POST.get('payment_mode')
        payment_status = request.POST.get('payment_status')
        service_status = 'Pending'
        ref_no = f"REF-942-{random.randint(100000000, 999999999)}"
        id_proof = request.FILES.get('id_proof')
        address_proof = request.FILES.get('address_proof')
        photo = request.FILES.get('photo')

        try:
            customer = Customer.objects.get(id=customer_id, created_by=request.user)  # Use `created_by` instead of `added_by`
        except Customer.DoesNotExist:
            messages.error(request, "Invalid customer selected.")
            return redirect('add_billing')

        BillingDetails.objects.create(
            user=request.user,
            ref_no=ref_no,
            customer=customer,
            service=service,
            payment_mode=payment_mode,
            payment_status=payment_status,
            service_status=service_status,
            id_proof=id_proof,
            address_proof=address_proof,
            photo=photo,
        )

        messages.success(request, "Billing added successfully.")
        return redirect('retailer_view_billing')

    # Render the form
    customers = Customer.objects.filter(created_by=request.user) 
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

    # Debugging: Print invoice IDs
    for bill in billing_details:
        print(f"Invoice ID: {bill.id}")

    # Pagination (e.g., 10 billing records per page)
    paginator = Paginator(billing_details, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'retailer_dashboard/view_billing.html', {'page_obj': page_obj})









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
            messages.info(request, "Your request is pending from the Bank. Please wait for approval.")
    except BankingPortalAccessRequest.DoesNotExist:
        # Create a new request if none exists
        if request.method == 'POST':
            BankingPortalAccessRequest.objects.create(user=request.user)
            messages.success(request, "Your request has been submitted successfully.")
            return redirect('banking_portal_request') # Redirect to the dashboard after request submission

    return render(request, 'retailer_dashboard/request_access.html')



# Edit Invoice

@login_required
@role_required(['retailer'])
def get_retailer_monthly_deductions(request):
    """Get monthly wallet deductions data for the retailer dashboard."""
    today = timezone.now()
    current_year = today.year
    current_month = today.month
    
    # Get all months in the current year up to current month
    months_data = []
    labels = []
    
    for month in range(1, current_month + 1):
        # Get total deductions for this month
        monthly_deductions = Transaction.objects.filter(
            user=request.user,
            transaction_type="Debit",
            created_at__year=current_year,
            created_at__month=month
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Format month name
        month_name = calendar.month_abbr[month]
        
        months_data.append(float(monthly_deductions))
        labels.append(f"{month_name} {current_year}")

    return JsonResponse({
        'labels': labels,
        'data': months_data,
        'current_month_deductions': float(months_data[-1]) if months_data else 0
    })


@login_required
@role_required(['retailer'])
def get_services_distribution(request):
    """Get services distribution data for the retailer dashboard."""
    current_year = timezone.now().year
    
    # Get service distribution data
    service_distribution = BillingDetails.objects.filter(
        user=request.user,
        billing_date__year=current_year
    ).values('service__service_name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Format the service distribution data for the doughnut chart
    labels = []
    data = []
    for item in service_distribution:
        if item['service__service_name']:  # Check for null service names
            labels.append(item['service__service_name'])
            data.append(item['count'])

    return JsonResponse({
        'labels': labels,
        'data': data
    })


@role_required(['retailer'])
@login_required
def recharge_plans_view(request):
    """
    View to display available recharge plans to the retailer.
    """
    return render(request, 'recharge_plans.html')
