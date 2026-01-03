from django.shortcuts import render, redirect, get_object_or_404
from dashboard.utils import role_required, generate_qr
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from dashboard.models import Notification
from dashboard.models import Customer, CustomUser
from django.contrib import messages
from dashboard.models import Service, BillingDetails,Transaction, Wallet, Transaction
from dashboard.forms import AddCustomerForm
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
from dashboard.models import CSCService, CSCServiceRequest
from dashboard.forms import CSCServiceRequestForm
from dashboard.forms import AddCustomerForm
from dashboard.models import Retailer2BillingDetails
from dashboard.forms import Retailer2BillingForm, BillingDetailsForm, BillingForm






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

    # Calculate total sales (sum of all Credit transactions for this user)
    total_sales = Transaction.objects.filter(user=request.user, transaction_type='Credit').aggregate(total=Sum('amount'))['total'] or 0

    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')[:7]  # Sort by newest first
    
    # Pass total_services to the context
    context = {
        'notifications': notifications,
        'total_services': total_services,
        'wallet_balance': wallet_balance,
        'total_billings': total_billings,  # Include total billings count
        'billing_details': billing_details,  # Include billing details for the retailer
        'total_sales': total_sales,  # Add total sales to context
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

@login_required
@role_required(['retailer'])
def retailer_invoice(request, billing_id):
    """Generate and display invoice for Retailer billing with editable amount"""
    try:
        billing = BillingDetails.objects.get(id=billing_id, user=request.user)
    except BillingDetails.DoesNotExist:
        messages.error(request, "Invoice not found.")
        return redirect('retailer_view_billing')
    
    # Handle amount update if POST request
    if request.method == 'POST':
        new_amount = request.POST.get('amount')
        if new_amount:
            try:
                billing.amount = Decimal(new_amount)
                billing.save()
                messages.success(request, "Invoice amount updated successfully!")
            except (ValueError, TypeError):
                messages.error(request, "Invalid amount entered.")
        return redirect('retailer_invoice', billing_id=billing_id)
    
    # Get user details (retailer)
    user = request.user
    customer = billing.customer
    
    # Generate invoice_id if not exists
    if not billing.invoice_id:
        import uuid
        billing.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        billing.save()
    
    context = {
        'billing': billing,
        'user': user,
        'customer': customer,
        'service': billing.service,
        'invoice_id': billing.invoice_id or billing.ref_no,
        'billing_date': billing.billing_date,
    }
    
    return render(request, 'retailer_dashboard/invoice.html', context)






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
            return redirect('https://grahakepay.com/login')  # Redirect to banking portal if already active
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
    user = request.user
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum
    import calendar
    
    today = timezone.now()
    monthly_labels = []
    monthly_deductions = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month = month_date.month
        year = month_date.year
        label = month_date.strftime('%b %Y')
        monthly_labels.append(label)
        month_deduction = Transaction.objects.filter(
            user=user,
            transaction_type='Debit',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_deductions.append(float(month_deduction))
    return JsonResponse({
        'labels': monthly_labels,
        'deductions': monthly_deductions
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





@login_required
@role_required(['retailer'])
def get_retailer_monthly_sales(request):
    user = request.user
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum

    today = timezone.now()
    monthly_labels = []
    monthly_sales = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month = month_date.month
        year = month_date.year
        label = month_date.strftime('%b %Y')
        monthly_labels.append(label)
        # Sum of all Credit transactions for this month
        month_sales = Transaction.objects.filter(
            user=user,
            transaction_type='Credit',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_sales.append(float(month_sales))
    return JsonResponse({
        'labels': monthly_labels,
        'sales': monthly_sales
    })


@login_required
@role_required(['retailer'])
def get_retailer_monthly_billing(request):
    user = request.user
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now()
    monthly_labels = []
    monthly_billing = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month = month_date.month
        year = month_date.year
        label = month_date.strftime('%b %Y')
        monthly_labels.append(label)
        count = BillingDetails.objects.filter(
            user=user,
            billing_date__year=year,
            billing_date__month=month
        ).count()
        monthly_billing.append(count)
    return JsonResponse({
        'labels': monthly_labels,
        'billing': monthly_billing
    })

@role_required(['retailer_2'])
def retailer_2_dashboard(request):
    # Fetch notifications for the current user
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0.0
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Count total services
    total_services = Service.objects.filter(status='active').count()
    
    # Count total billings for the retailer 2.0
    total_billings = BillingDetails.objects.filter(user=request.user).count()

    # Calculate total sales (sum of all Credit transactions for this user)
    total_sales = Transaction.objects.filter(user=request.user, transaction_type='Credit').aggregate(total=Sum('amount'))['total'] or 0

    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')[:7]
    
    # Get CSC services for dynamic display
    csc_services = CSCService.objects.filter(is_active=True).order_by('service_name')
    
    context = {
        'notifications': notifications,
        'total_services': total_services,
        'wallet_balance': wallet_balance,
        'total_billings': total_billings,
        'billing_details': billing_details,
        'total_sales': total_sales,
        'csc_services': csc_services,
    }
    return render(request, 'retailer_2_dashboard/retailer_2_dashboard.html', context)

# CSC 2.0 Retailer Views
@login_required
@role_required(['retailer_2'])
def csc_services_view(request):
    """View available CSC services for Retailer 2.0"""
    services = CSCService.objects.filter(is_active=True).order_by('service_name')
    
    # Get retailer's wallet balance
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0
    
    context = {
        'services': services,
        'wallet_balance': wallet_balance,
    }
    return render(request, 'retailer_2_dashboard/csc_services.html', context)

@login_required
@role_required(['retailer_2'])
def csc_service_detail(request, service_id):
    """View details of a specific CSC service"""
    service = get_object_or_404(CSCService, id=service_id, is_active=True)
    
    # Get retailer's wallet balance
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0
    
    context = {
        'service': service,
        'wallet_balance': wallet_balance,
    }
    return render(request, 'retailer_2_dashboard/csc_service_detail.html', context)

@login_required
@role_required(['retailer_2'])
def csc_request_service(request, service_id):
    """Request a CSC service"""
    service = get_object_or_404(CSCService, id=service_id, is_active=True)
    
    # Check if retailer has sufficient wallet balance
    try:
        wallet = Wallet.objects.get(user=request.user)
        if wallet.balance < service.wallet_deduction:
            messages.error(request, f"Insufficient wallet balance. Required: ₹{service.wallet_deduction}, Available: ₹{wallet.balance}")
            return redirect('csc_service_detail', service_id=service_id)
    except Wallet.DoesNotExist:
        messages.error(request, "Wallet not found. Please contact support.")
        return redirect('csc_services_view')
    
    if request.method == 'POST':
        form = CSCServiceRequestForm(request.POST)
        if form.is_valid():
            # Create the service request
            service_request = form.save(commit=False)
            service_request.service = service
            service_request.retailer = request.user
            service_request.amount_paid = service.price
            service_request.wallet_deduction = service.wallet_deduction
            
            # Deduct from wallet
            wallet.balance -= service.wallet_deduction
            wallet.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                amount=service.wallet_deduction,
                transaction_type="Debit",
                balance_after_transaction=wallet.balance,
                description=f"CSC Service: {service.service_name} - {service_request.customer_name}"
            )
            
            service_request.save()
            messages.success(request, f"CSC service request submitted successfully. ₹{service.wallet_deduction} deducted from wallet.")
            return redirect('csc_my_requests')
    else:
        form = CSCServiceRequestForm(initial={'service': service})
    
    context = {
        'form': form,
        'service': service,
        'wallet_balance': wallet.balance,
    }
    return render(request, 'retailer_2_dashboard/csc_request_service.html', context)

@login_required
@role_required(['retailer_2'])
def csc_my_requests(request):
    """View retailer's CSC service requests"""
    requests = CSCServiceRequest.objects.filter(retailer=request.user).order_by('-created_at')
    
    context = {
        'requests': requests,
    }
    return render(request, 'retailer_2_dashboard/csc_my_requests.html', context)

# Retailer 2.0 Customer Management Views
@login_required
@role_required(['retailer_2'])
def retailer_2_add_customer(request):
    """Add a new customer for Retailer 2.0"""
    if request.method == 'POST':
        form = AddCustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('retailer_2_view_customer')
    else:
        form = AddCustomerForm()
    
    context = {
        'form': form,
        'title': 'Add Customer - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/add_customer.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_view_customer(request):
    """View all customers for Retailer 2.0"""
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Filter customers based on search query
    customers = Customer.objects.filter(created_by=request.user)
    
    if search_query:
        customers = customers.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(mobile__icontains=search_query)
        )
    
    # Order by creation date (newest first)
    customers = customers.order_by('-created_at')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'title': 'View Customers - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/view_customer.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_edit_customer(request, customer_id):
    """Edit a customer for Retailer 2.0"""
    customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    
    if request.method == 'POST':
        form = AddCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('retailer_2_view_customer')
    else:
        form = AddCustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/edit_customer.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_delete_customer(request, customer_id):
    """Delete a customer for Retailer 2.0"""
    customer = get_object_or_404(Customer, id=customer_id, created_by=request.user)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('retailer_2_view_customer')
    
    context = {
        'customer': customer,
        'title': 'Delete Customer - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/delete_customer.html', context)

# Retailer 2.0 Billing Management Views
@login_required
@role_required(['retailer_2'])
def retailer_2_add_billing(request):
    """Add a new billing for Retailer 2.0 with wallet deduction"""
    if request.method == 'POST':
        # Fetch the logged-in user's wallet
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found. Please contact support.")
            return redirect('retailer_2_dashboard')

        # Fetch the selected service
        service_id = request.POST.get('service')
        try:
            service = CSCService.objects.get(id=service_id, is_active=True)
        except CSCService.DoesNotExist:
            messages.error(request, "Invalid service selected.")
            return redirect('retailer_2_add_billing')

        # Get custom price from form, or use service default price
        custom_price = request.POST.get('amount')
        if custom_price:
            try:
                service_price = Decimal(custom_price)
            except (ValueError, TypeError):
                service_price = service.wallet_deduction
        else:
            service_price = service.wallet_deduction

        # Check wallet balance
        if wallet.balance < service_price:
            messages.error(
                request,
                f"Insufficient balance to add billing for this service. Required: ₹{service_price}, Available: ₹{wallet.balance}. Please recharge your wallet."
            )
            return redirect('retailer_2_add_billing')

        # Deduct service price from the wallet
        wallet.balance -= service_price
        wallet.save()

        # Log the transaction
        Transaction.objects.create(
            user=request.user,
            amount=service_price,
            transaction_type="Debit",
            balance_after_transaction=wallet.balance,
            description=f"Retailer 2.0 Billing: {service.service_name}",
        )

        # Create Billing Details
        customer_id = request.POST.get('customer')
        payment_mode = request.POST.get('payment_mode')
        payment_status = request.POST.get('payment_status')
        service_status = 'Pending'
        ref_no = f"REF-942-{random.randint(100000000, 999999999)}"
        # Generate unique invoice ID
        import uuid
        invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        id_proof = request.FILES.get('id_proof')
        address_proof = request.FILES.get('address_proof')
        photo = request.FILES.get('photo')
        pan_card = request.POST.get('pan_card', '')
        banking = request.FILES.get('banking')
        others = request.FILES.get('others')
        service_notes = request.POST.get('service_notes', '')

        try:
            customer = Customer.objects.get(id=customer_id, created_by=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "Invalid customer selected.")
            return redirect('retailer_2_add_billing')

        billing = Retailer2BillingDetails.objects.create(
            user=request.user,
            ref_no=ref_no,
            customer=customer,
            service=service,
            amount=service_price,  # Save custom price
            payment_mode=payment_mode,
            payment_status=payment_status,
            service_status=service_status,
            invoice_id=invoice_id,
            id_proof=id_proof,
            address_proof=address_proof,
            photo=photo,
            pan_card=pan_card,
            banking=banking,
            others=others,
            service_notes=service_notes,
        )

        messages.success(request, f"Billing added successfully! ₹{service_price} deducted from wallet.")
        # Redirect to invoice page
        return redirect('retailer_2_invoice', billing_id=billing.id)

@login_required
@role_required(['retailer_2'])
def retailer_2_invoice(request, billing_id):
    """Generate and display invoice for Retailer 2.0 billing"""
    try:
        billing = Retailer2BillingDetails.objects.get(id=billing_id, user=request.user)
    except Retailer2BillingDetails.DoesNotExist:
        messages.error(request, "Invoice not found.")
        return redirect('retailer_2_view_billing')
    
    # Handle POST request for amount update
    if request.method == 'POST':
        try:
            new_amount = float(request.POST.get('amount', 0))
            if new_amount > 0:
                billing.amount = new_amount
                billing.save()
                messages.success(request, f"Invoice amount updated to ₹{new_amount:.2f}")
            else:
                messages.error(request, "Amount must be greater than 0.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
        return redirect('retailer_2_invoice', billing_id=billing_id)
    
    # Get user details (retailer)
    user = request.user
    customer = billing.customer
    
    # Generate invoice_id if not exists
    if not billing.invoice_id:
        import uuid
        billing.invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        billing.save()
    
    context = {
        'billing': billing,
        'user': user,
        'customer': customer,
        'service': billing.service,
        'invoice_id': billing.invoice_id or billing.ref_no,
        'billing_date': billing.billing_date,
    }
    
    return render(request, 'retailer_2_dashboard/invoice.html', context)

    # Render the form
    customers = Customer.objects.filter(created_by=request.user).order_by('full_name')
    services = CSCService.objects.filter(is_active=True).order_by('service_name')
    
    # Get wallet balance
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0.00
    
    return render(request, 'retailer_2_dashboard/add_billing.html', {
        'customers': customers,
        'services': services,
        'wallet_balance': wallet_balance,
    })

@login_required
@role_required(['retailer_2'])
def retailer_2_view_billing(request):
    """View all billings for Retailer 2.0"""
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Filter billings based on search query
    billings = Retailer2BillingDetails.objects.filter(user=request.user)
    
    if search_query:
        billings = billings.filter(
            Q(ref_no__icontains=search_query) |
            Q(customer__full_name__icontains=search_query) |
            Q(service__service_name__icontains=search_query) |
            Q(payment_status__icontains=search_query) |
            Q(service_status__icontains=search_query)
        )
    
    # Order by billing date (newest first)
    billings = billings.order_by('-billing_date')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(billings, 10)  # Show 10 billings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'billings': page_obj,
        'search_query': search_query,
        'title': 'View Billing - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/view_billing.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_view_billing_details(request, billing_id):
    """View billing details for Retailer 2.0"""
    billing = get_object_or_404(Retailer2BillingDetails, id=billing_id, user=request.user)
    context = {
        'billing': billing,
        'title': 'Billing Details - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/view_billing_details.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_edit_billing(request, billing_id):
    """Edit a billing for Retailer 2.0"""
    billing = get_object_or_404(Retailer2BillingDetails, id=billing_id, user=request.user)
    if request.method == 'POST':
        form = Retailer2BillingForm(request.POST, request.FILES, instance=billing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Billing updated successfully!')
            return redirect('retailer_2_view_billing')
    else:
        form = Retailer2BillingForm(instance=billing)
    
    customers = Customer.objects.filter(created_by=request.user).order_by('full_name')
    services = CSCService.objects.filter(is_active=True).order_by('service_name')
    form.fields['customer'].queryset = customers
    form.fields['service'].queryset = services
    
    context = {
        'form': form,
        'billing': billing,
        'customers': customers,
        'services': services,
        'title': 'Edit Billing - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/edit_billing.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_delete_billing(request, billing_id):
    """Delete a billing for Retailer 2.0"""
    billing = get_object_or_404(Retailer2BillingDetails, id=billing_id, user=request.user)
    
    if request.method == 'POST':
        billing.delete()
        messages.success(request, 'Billing deleted successfully!')
        return redirect('retailer_2_view_billing')
    
    context = {
        'billing': billing,
        'title': 'Delete Billing - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/delete_billing.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_wallet_recharge_view(request):
    """Wallet recharge view for Retailer 2.0 with offer cards"""
    retailer = request.user  # Get the logged-in retailer
    user_name = retailer.full_name
    qr_code_path = os.path.join('static', 'qr_codes', f"{user_name.replace(' ', '_')}_qr.png")

    return render(request, 'retailer_2_dashboard/wallet_recharge.html', {
        'user_name': user_name,
        'qr_code': qr_code_path,
    })

@login_required
@role_required(['retailer_2'])
def retailer_2_view_transactions(request):
    """View transactions for Retailer 2.0"""
    # Fetch transactions for the logged-in retailer
    retailer = request.user
    transactions = Transaction.objects.filter(user=retailer).order_by('-created_at')

    # Add pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
        'title': 'View Transactions - Retailer 2.0'
    }

    return render(request, 'retailer_2_dashboard/view_transactions.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_edit_profile(request):
    """Edit profile for Retailer 2.0"""
    if request.method == 'POST':
        # Update user profile fields
        user = request.user
        user.full_name = request.POST.get('full_name', user.full_name)
        user.mobile_number = request.POST.get('mobile_number', user.mobile_number)
        user.address = request.POST.get('address', user.address)
        user.state = request.POST.get('state', user.state)
        user.city = request.POST.get('city', user.city)
        user.postcode = request.POST.get('postcode', user.postcode)
        user.gender = request.POST.get('gender', user.gender)
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            user.profile_photo = request.FILES['profile_photo']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('retailer_2_edit_profile')
    
    context = {
        'user': request.user,
        'title': 'Edit Profile - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/edit_profile.html', context)

@login_required
@role_required(['retailer_2'])
def retailer_2_settings(request):
    """Settings page for Retailer 2.0"""
    context = {
        'user': request.user,
        'title': 'Settings - Retailer 2.0'
    }
    return render(request, 'retailer_2_dashboard/settings.html', context)

