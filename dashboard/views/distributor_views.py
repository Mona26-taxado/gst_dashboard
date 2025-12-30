from django.shortcuts import render, redirect, get_object_or_404
from dashboard.utils import role_required
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
import json
from django.db.models import Sum, F
from django.http import HttpResponseForbidden, HttpResponse
from dashboard.models import CustomUser
import qrcode
from django.http import Http404
import logging
import os
from dashboard.models import BankingPortalAccessRequest
from django.db.models import Q
from dashboard.forms import AddGSKForm 
from decimal import Decimal # Ensure this form is defined or imported
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta





@role_required(['distributor'])
def distributor_dashboard(request):
    return render(request, 'distributor_dashboard/distributor_dashboard.html')




def pin_entry(request):
    """
    View for managing PIN entry.
    """
    return render(request, 'pin_entry.html')









@role_required(['distributor'])
def distributor_dashboard(request):
    # Fetch notifications for the current user
    try:
        wallet = Wallet.objects.get(user=request.user)
        wallet_balance = wallet.balance
    except Wallet.DoesNotExist:
        wallet_balance = 0.0
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Count total services
    total_services = Service.objects.filter(status='active').count()  # Assuming active status filtering
    
    # Count total billings for the distributor
    total_billings = BillingDetails.objects.filter(user=request.user).count()

    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')[:7]  # Sort by newest first

    # Count total retailers referred by this distributor
    total_retailers = CustomUser.objects.filter(referred_by=request.user, role='retailer').count()
    
    # Get current month's data
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_services = Service.objects.filter(
        billing_date__month=current_month,
        billing_date__year=current_year
    ).count()
    
    monthly_billing = BillingDetails.objects.filter(
        user=request.user,
        billing_date__month=current_month,
        billing_date__year=current_year
    ).aggregate(total=Sum(F('service__price')))['total'] or 0

    # Prepare data for doughnut chart (Total Sales Distribution)
    service_distribution = {
        'labels': ['Services', 'Billings', 'Retailers'],
        'data': [total_services, total_billings, total_retailers]
    }

    # Prepare data for bar chart (Monthly Performance)
    yearly_data = {
        'labels': [],
        'data': []
    }
    
    # Get last 6 months data
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=i*30)
        month_name = month_date.strftime('%b')
        yearly_data['labels'].append(month_name)
        
        # Get billing amount for this month
        month_billing = BillingDetails.objects.filter(
            billing_date__month=month_date.month,
            billing_date__year=month_date.year
        ).aggregate(total=Sum(F('service__price')))['total'] or 0
        
        yearly_data['data'].append(float(month_billing))

    # Get year range for selector
    year_range = range(current_year-2, current_year+1)

    # Pass total_services to the context
    context = {
        'notifications': notifications,
        'total_services': total_services,
        'wallet_balance': wallet_balance,
        'total_billings': total_billings,  # Include total billings count
        'billing_details': billing_details,  # Include billing details for the retailer
        'total_retailers': total_retailers,  # Add total retailers to context
        'monthly_services': monthly_services,
        'monthly_billing': monthly_billing,
        'yearly_data': json.dumps(yearly_data),
        'service_distribution': json.dumps(service_distribution),
        'year_range': year_range,
        'current_year': current_year,
    }
    print('DASHBOARD CONTEXT:', context)  # Debug print
    return render(request, 'distributor_dashboard/distributor_dashboard.html', context)




def pin_entry(request):
    """
    View for managing PIN entry.
    """
    return render(request, 'pin_entry.html')









from django.db.models import Q
from dashboard.forms import AddGSKForm  # Ensure this form is defined or imported

@login_required
@role_required(['distributor'])
def add_gsk(request):
    """
    Distributor-specific add GSK view.
    """
    if request.method == 'POST':
        form = AddGSKForm(request.POST)
        if form.is_valid():
            try:
                # Automatically set the distributor as the referred_by field
                form.instance.referred_by = request.user
                form.instance.distributor = request.user
                # Save the GSK
                gsk = form.save()
                messages.success(request, "GSK added successfully.")
                return redirect('distributor_view_gsk')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AddGSKForm()

    return render(request, 'distributor_dashboard/add_gsk.html', {'form': form})





@login_required
@role_required(['distributor'])
def view_gsk(request):
    """
    Distributor-specific view GSKs.
    """
    search_query = request.GET.get('search', '')

    # Fetch GSKs linked to the logged-in distributor
    gsk_list = CustomUser.objects.filter(referred_by=request.user).order_by('-created_at')
    if search_query:
        # Apply search filters
        gsk_list = gsk_list.filter(
            Q(username__icontains=search_query) |
            Q(branch_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    paginator = Paginator(gsk_list, 10)  # Paginate results (10 per page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate the serial number offset for infinite numbering
    serial_start = (page_obj.number - 1) * paginator.per_page

    context = {
        'gsk_list': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
        'serial_start': serial_start,
    }
    return render(request, 'distributor_dashboard/view_gsk.html', context)


@login_required
@role_required(['distributor'])
def edit_gsk(request, gsk_id):
    user = get_object_or_404(CustomUser, id=gsk_id)
    if request.method == 'POST':
        form = AddGSKForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "GSK user details updated successfully.")
            return redirect('distributor_view_gsk')
    else:
        form = AddGSKForm(instance=user)

    return render(request, 'distributor_dashboard/edit_gsk.html', {'form': form, 'gsk': user})








@role_required(['distributor'])
@login_required
def delete_gsk(request, gsk_id):
    """
    Allows a distributor to delete a GSK they created.
    """
    gsk = get_object_or_404(CustomUser, id=gsk_id, referred_by=request.user, role='retailer')  # Ensure it's a retailer referred by this distributor
    
    # Ensure the user is authorized to delete this GSK
    if gsk.referred_by != request.user:
        messages.error(request, "You are not authorized to delete this GSK.")
        return redirect('distributor_view_gsk')

    gsk.delete()
    messages.success(request, "GSK deleted successfully!")
    return redirect('distributor_view_gsk')








@role_required(['distributor', 'distributor', 'master_distributor'])
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
    return render(request, 'distributor_dashboard/view_services.html', context)






# Add Customer
@role_required(['distributor'])
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
            return redirect('distributor_add_billing')  # Redirect after successful save
    else:
        form = AddCustomerForm()
    return render(request, 'distributor_dashboard/add_customer.html', {'form': form})








@role_required(['distributor'])
@login_required
def view_customer(request):
    # Ensure the logged-in user is a distributor
    if request.user.role != 'distributor':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch only the customers created by the logged-in distributor
    customers = Customer.objects.filter(created_by=request.user).order_by('-created_at')  # Sort by newest first

    # Pagination (7 customers per page)
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the global serial number for the current page
    start_index = page_obj.start_index()

    return render(request, 'distributor_dashboard/view_customer.html', {
        'page_obj': page_obj,
        'start_index': start_index,
    })





@role_required(['distributor'])  # Restrict access to specific roles
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
                return render(request, 'distributor_dashboard/edit_customer.html', {'customer': customer})
        else:
            customer.dob = None  # Allow clearing DOB if not provided

        # Save the updated customer
        print("Before Save:", customer)  # Debug before save
        customer.save()
        print("After Save:", customer)  # Debug after save

        messages.success(request, "Customer updated successfully!")
        return redirect('distributor_view_customer')  # Redirect after successful update

    # Render the edit form
    return render(request, 'distributor_dashboard/edit_customer.html', {'customer': customer})








@role_required(['distributor'])
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, "Customer deleted successfully.")
    return redirect('distributor_view_customer')  # Ensure the name matches the URL pattern in urls.py






@role_required(['distributor'])
def add_billing(request):
    if request.method == 'POST':
        # Fetch the logged-in user's wallet
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found. Please contact support.")
            return redirect('distributor_dashboard/add_billing.html')

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
            return redirect('distributor_dashboard/add_billing.html')

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
        return redirect('distributor_view_billing')

    # Render the form
    customers = Customer.objects.filter(created_by=request.user) 
    services = Service.objects.filter(status='active')
    return render(request, 'distributor_dashboard/add_billing.html', {
        'customers': customers,
        'services': services,
    })








# View Billing Details
@role_required(['distributor'])
@login_required
def view_billing(request):
    # Ensure the logged-in user is a distributor
    if request.user.role != 'distributor':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch only the billing records created by the logged-in distributor
    billing_details = BillingDetails.objects.filter(user=request.user).order_by('-billing_date')  # Sort by newest first

    # Pagination (e.g., 10 billing records per page)
    paginator = Paginator(billing_details, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'distributor_dashboard/view_billing.html', {
        'page_obj': page_obj,
    })








# View for editing billing details
# View Billing Details
def view_billing_details(request, billing_id):
    billing_details = get_object_or_404(BillingDetails, id=billing_id)
    customer = billing_details.customer  # Get the customer details
    distributor = request.user  # Assuming the logged-in user is the distributor
    
    context = {
        'billing_details': billing_details,
        'customer': customer,
        'distributor': distributor,
    }
    return render(request, 'distributor_dashboard/view_billing_details.html', context)






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
            # Redirect to the distributor's View Billing page
            return redirect('distributor_view_billing')
    else:
        form = BillingDetailsForm(instance=billing_details)

    return render(
        request,
        'distributor_dashboard/edit_billing.html',
        {
            'form': form,
            'billing_details': billing_details,
            'services': services,  # For service dropdown
        },
    )



def view_wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    return render(request, "distributor_dashboard/wallet.html", {"wallet": wallet})





@login_required
def distributor_view_transactions(request):
    if request.user.role != 'distributor':
        return HttpResponseForbidden("You are not authorized to view this page.")

    # Fetch transactions for the logged-in distributor
    distributor = request.user
    transactions = Transaction.objects.filter(user=distributor).order_by('-created_at')

    # Add pagination
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
    }

    return render(request, 'distributor_dashboard/view_transactions.html', context)








@role_required(['distributor'])
def wallet_recharge_view(request):
    distributor = request.user  # Get the logged-in distributor
    user_name = distributor.full_name
    qr_code_path = os.path.join('static', 'qr_codes', f"{user_name.replace(' ', '_')}_qr.png")

    return render(request, 'distributor_dashboard/wallet_recharge.html', {
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
            messages.info(request, "Your request is pending. Please wait for approval.")
    except BankingPortalAccessRequest.DoesNotExist:
        # Create a new request if none exists
        if request.method == 'POST':
            BankingPortalAccessRequest.objects.create(user=request.user)
            messages.success(request, "Your request has been submitted successfully.")
            return redirect('banking_portal_request') # Redirect to the dashboard after request submission

    return render(request, 'distributor_dashboard/request_access.html')





@login_required
@role_required(['distributor'])
def transfer_money(request):
    try:
        # Ensure distributor has a wallet
        distributor_wallet, created = Wallet.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            retailer_id = request.POST.get('retailer_id')
            amount = Decimal(request.POST.get('amount'))

            # Check if retailer exists and is created by this distributor
            try:
                retailer = CustomUser.objects.get(id=retailer_id, referred_by=request.user, role='retailer')
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid retailer selected.")
                return redirect('transfer_money')

            # Validate sufficient wallet balance
            if distributor_wallet.balance < amount:
                messages.error(request, f"Insufficient wallet balance. Your current balance is ₹{distributor_wallet.balance}.")
                return redirect('transfer_money')

            # Get retailer's wallet or create it if not present
            retailer_wallet, created = Wallet.objects.get_or_create(user=retailer)

            # Perform the money transfer
            distributor_wallet.balance -= amount
            retailer_wallet.balance += amount
            distributor_wallet.save()
            retailer_wallet.save()

            # Log the transaction
            Transaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type="Debit",
                balance_after_transaction=distributor_wallet.balance,
                description=f"Transferred to retailer: {retailer.full_name}"
            )
            Transaction.objects.create(
                user=retailer,
                amount=amount,
                transaction_type="Credit",
                balance_after_transaction=retailer_wallet.balance,
                description=f"Received from distributor: {request.user.full_name}"
            )

            messages.success(request, f"Successfully transferred ₹{amount} to {retailer.full_name}.")
            return redirect('transfer_money')

        # Fetch all retailers created by the logged-in distributor
        retailers = CustomUser.objects.filter(referred_by=request.user, role='retailer')
        return render(request, 'distributor_dashboard/transfer_money.html', {'retailers': retailers, 'wallet_balance': distributor_wallet.balance})

    except Wallet.DoesNotExist:
        messages.error(request, "Wallet not found for your account. Please contact support.")
        return redirect('distributor_dashboard')


@role_required(['distributor'])
def get_distributor_dashboard_data(request):
    """Get data for distributor dashboard charts and statistics."""
    today = timezone.now()
    current_month = today.month
    current_year = today.year

    # Get monthly billing data
    monthly_billing = BillingDetails.objects.filter(
        user=request.user,
        billing_date__year=current_year,
        billing_date__month=current_month
    ).aggregate(
        total_amount=Sum('price'),
        total_billings=Count('id')
    )

    # Get yearly billing data
    yearly_billing = BillingDetails.objects.filter(
        user=request.user,
        billing_date__year=current_year
    ).aggregate(
        total_amount=Sum('price'),
        total_billings=Count('id')
    )

    # Get service distribution data
    service_distribution = BillingDetails.objects.filter(
        user=request.user,
        billing_date__year=current_year
    ).values('service__service_name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Get monthly trend (last 6 months)
    months_data = []
    labels = []
    
    for i in range(5, -1, -1):
        target_date = today - timedelta(days=i*30)
        month = target_date.month
        year = target_date.year
        
        monthly_amount = BillingDetails.objects.filter(
            user=request.user,
            billing_date__year=year,
            billing_date__month=month
        ).aggregate(
            total=Sum('price')
        )['total'] or 0
        
        month_name = target_date.strftime('%b-%Y')
        months_data.append(float(monthly_amount))
        labels.append(month_name)

    # Format the service distribution data for the doughnut chart
    service_labels = []
    service_data = []
    for item in service_distribution:
        service_labels.append(item['service__service_name'])
        service_data.append(item['count'])

    return JsonResponse({
        'monthly': {
            'total_amount': float(monthly_billing['total_amount'] or 0),
            'total_billings': monthly_billing['total_billings'] or 0
        },
        'yearly': {
            'total_amount': float(yearly_billing['total_amount'] or 0),
            'total_billings': yearly_billing['total_billings'] or 0
        },
        'service_distribution': {
            'labels': service_labels,
            'data': service_data
        },
        'trend': {
            'labels': labels,
            'data': months_data
        }
    })

@login_required
@role_required(['distributor'])
def get_distributor_monthly_billing(request):
    user = request.user
    today = timezone.now()
    monthly_labels = []
    monthly_billing = []
    retailers = CustomUser.objects.filter(referred_by=user, role='retailer')
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i*30)
        month = month_date.month
        year = month_date.year
        label = month_date.strftime('%b %Y')
        monthly_labels.append(label)
        count = BillingDetails.objects.filter(
            user__in=retailers,
            billing_date__year=year,
            billing_date__month=month
        ).count()
        monthly_billing.append(count)
    return JsonResponse({
        'labels': monthly_labels,
        'billing': monthly_billing
    })

@login_required
@role_required(['distributor'])
def get_distributor_monthly_deductions(request):
    user = request.user
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

