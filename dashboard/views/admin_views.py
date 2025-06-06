from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from dashboard.forms import AddGSKForm
from dashboard.forms import ServiceForm
from dashboard.models import Service, Notification, BankingPortalAccessRequest
from dashboard.models import CustomUser
from django.core.paginator import Paginator
from dashboard.utils import role_required
from django.contrib.auth.models import User
from django.contrib import messages
import random
from django.db import IntegrityError
from dashboard.models import Service, BillingDetails, Wallet, Transaction
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.db.models import F, Q
from django.db.models.signals import pre_delete
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied





@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'admin_dashboard/admin_home.html')






  # Allow only admins to access this view
@login_required
@role_required(['admin'])
def admin_dashboard(request):
    # Count all relevant GSK entries
    
    total_bills = BillingDetails.objects.count()
    total_centers = CustomUser.objects.filter(role__in=['retailer', 'distributor', 'master_distributor']).count()
    total_services = Service.objects.count()
    billing_details = BillingDetails.objects.all().order_by('-id')[:7]
    # Add more stats as needed

    
    context = {
        'total_bills': total_bills,
        'total_centers': total_centers,
        'total_services': total_services,
        'billing_details': billing_details,
    }

    return render(request, 'admin_dashboard/admin_home.html', context)





@login_required
@role_required(['admin'])
def add_gsk(request):
    distributors = CustomUser.objects.filter(role__in=['distributor', 'master_distributor'], is_active=True)

    if request.method == 'POST':
        form = AddGSKForm(request.POST)
        if form.is_valid():
            try:
                # Assign referred_by if applicable
                referred_by_id = request.POST.get('referred_by')
                if referred_by_id:
                    referred_by = CustomUser.objects.get(id=referred_by_id)
                    form.instance.referred_by = referred_by

                # Save user
                user = form.save()
                messages.success(request, "GSK user added successfully.")
                return redirect('admin_view_gsk')
            except CustomUser.DoesNotExist:
                messages.error(request, "Referred user does not exist.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AddGSKForm()

    return render(request, 'admin_dashboard/add_gsk.html', {'form': form, 'distributors': distributors})







#Pagination helps split large datasets into smaller, manageable chunks. Django's Paginator makes this easy.


@login_required
@role_required(['admin'])
def view_gsk(request):
    search_query = request.GET.get('search', '')
    
    # Fetch all relevant GSK users
    gsk_list = CustomUser.objects.filter(role__in=['retailer', 'distributor', 'master_distributor']).order_by('-created_at')
    if search_query:
        # Apply search filters
        gsk_list = gsk_list.filter(
            Q(username__icontains=search_query) |
            Q(branch_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    
    gsk_list = gsk_list.order_by('-created_at')  # Order by start_date or created_at


    paginator = Paginator(gsk_list, 10)  # Paginate results (10 per page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    # Calculate the serial number offset for infinite numbering
    serial_start = (page_obj.number - 1) * paginator.per_page

    # Debugging: Log retrieved GSK users
    print("GSK List:", gsk_list)

    context = {
        'gsk_list': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
        'serial_start': serial_start,
    }
    return render(request, 'admin_dashboard/view_gsk.html', context)






@login_required
@role_required(['admin'])
def edit_gsk(request, gsk_id):
    user = get_object_or_404(CustomUser, id=gsk_id)
    if request.method == 'POST':
        form = AddGSKForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "GSK user details updated successfully.")
            return redirect('admin_view_gsk')
    else:
        form = AddGSKForm(instance=user)

    return render(request, 'admin_dashboard/edit_gsk.html', {'form': form, 'gsk': user})











@login_required
@role_required(['admin'])
def delete_gsk(request, user_id):
    try:
        gsk_user = CustomUser.objects.get(id=user_id)
        gsk_user.delete()
        messages.success(request, "GSK user deleted successfully.")
    except CustomUser.DoesNotExist:
        messages.error(request, "GSK user does not exist.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    # Redirect to the GSK list view
    return redirect('admin_view_gsk')












@login_required
@role_required(['admin'])  # Ensure only admins can access this view
def add_service(request):
    if request.method == 'POST':
        # Debugging: Print all POST data
        print("POST Data:", request.POST)

        # Get data from the form
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        required_documents = request.POST.get('required_documents')
        status = request.POST.get('status')

        # Validate the fields
        if not service_name or not price or not status:
            messages.error(request, 'All fields are required.')
            return redirect('add_service')

        try:
            # Create the service
            service = Service.objects.create(
                service_name=service_name,
                price=float(price),  # Convert price to float
                required_documents=required_documents,
                status=status
            )
            service.save()
            messages.success(request, 'Service added successfully.')
            return redirect('view_services')
        except Exception as e:
            # Debugging: Print the error
            print("Error:", e)
            messages.error(request, f"An error occurred: {e}")
            return redirect('add_service')

    return render(request, 'admin_dashboard/add_service.html')








#Search allows users to filter GSKs or services based on specific criteria.


@login_required
@user_passes_test(lambda u: u.is_superuser or u.role == 'admin')  # Restrict to admins
def view_services(request):
    # Get all services for the admin
    search_query = request.GET.get('search', '')
    service_list = Service.objects.all().order_by('-id')  # Fetch all services
    
    # Search functionality
    if search_query:
        service_list = service_list.filter(service_name__icontains=search_query)
    
    
    # Pagination for services
    paginator = Paginator(service_list, 10)  # Show 7 services per page
    page_number = request.GET.get('page', 1)  # Default to the first page if not specified
    page_obj = paginator.get_page(page_number)
    
    # Calculate the starting index for each page
    start_index = (page_obj.number - 1) * paginator.per_page + 1

    context = {
        'service_list': page_obj,  # Pass paginated services
        'search_query': search_query,
        'start_index': start_index,  # Starting index for this page
    }
    return render(request, 'admin_dashboard/view_services.html', context)








@login_required
def edit_service(request, service_id):
    # Fetch the service object or return 404
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        # Bind the form with the POST data and the instance to update
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()  # Save the changes to the database
            return redirect('view_services')  # Redirect to view services page
        else:
            print("Form errors:", form.errors)  # Debugging: Check why the form is not valid
    else:
        # For GET request, show the current data in the form
        form = ServiceForm(instance=service)

    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'admin_dashboard/edit_service.html', context)


@login_required
@role_required(['admin'])
def delete_service(request, service_id):
    # Fetch the service
    service = get_object_or_404(Service, id=service_id)

    # Delete related BillingDetails records first
    related_billing_details = BillingDetails.objects.filter(service=service)
    related_billing_details.delete()  # Delete all related billing records

    # Delete the service
    service.delete()
    messages.success(request, "Service and its related billing details deleted successfully!")

    # Redirect to the services list
    return redirect('view_services')  # Update 'view_services' with your correct URL name



@login_required
def view_notifications(request):
    notifications = request.user.notifications.all()
    return render(request, 'admin_dashboard/notifications.html', {'notifications': notifications})






@login_required
def update_pin(request, user_id=None):
    # Restrict to admin users
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('admin_dashboard')

    # Fetch only users applicable for the PIN update
    users = CustomUser.objects.filter(role__in=['retailer', 'distributor', 'master_distributor'])
    selected_user = None

    if user_id:
        selected_user = get_object_or_404(CustomUser, id=user_id)

    # Handle POST request to update PIN
    if request.method == 'POST' and selected_user:
        new_pin = request.POST.get('pin')
        if new_pin and len(new_pin) == 4:  # Validate that PIN is a 4-digit number
            selected_user.pin = new_pin
            selected_user.save()
            messages.success(request, f'PIN updated successfully for {selected_user.full_name}.')
            return redirect('admin_dashboard')  # Redirect back to admin dashboard
        else:
            messages.error(request, 'Invalid PIN. Please enter a 4-digit PIN.')

    return render(request, 'admin_dashboard/update_pin.html', {
        'users': users,
        'selected_user': selected_user,
    })






@login_required
def pin_entry(request):
    user = request.user
    if not user.pin_updated:
        messages.error(request, 'Your PIN has not been updated. Contact admin.')
        return redirect('dashboard')  # Redirect if PIN is not updated

    if request.method == 'POST':
        entered_pin = request.POST.get('pin')
        if entered_pin == user.pin:
            messages.success(request, 'PIN verified successfully.')
            return redirect('additional_services')  # Redirect to the additional services page
        else:
            messages.error(request, 'Invalid PIN. Please try again.')

    return render(request, 'pin_entry.html')



@login_required
@role_required(['admin'])
def send_notifications(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        target_type = request.POST.get('target_type')  # 'individual' or 'group'
        target_user = request.POST.get('target_user')
        target_group = request.POST.get('target_group')

        if target_type == 'individual' and target_user:
            user = CustomUser.objects.get(id=target_user)
            Notification.objects.create(title=title, message=message, user=user)
            messages.success(request, f"Notification sent to {user.username}.")
        elif target_type == 'group' and target_group:
            users = CustomUser.objects.filter(role=target_group)
            for user in users:
                Notification.objects.create(title=title, message=message, user=user, group=target_group)
            messages.success(request, f"Notification sent to all {target_group}s.")
        else:
            messages.error(request, "Invalid target type or missing data.")

        return redirect('send_notifications')

    users = CustomUser.objects.exclude(role='admin')  # Exclude admins
    context = {
        'users': users,
    }
    return render(request, 'admin_dashboard/send_notifications.html', context)




@login_required
@role_required(['admin'])  # Restrict to admins
def manage_notifications(request):
    notifications = Notification.objects.all().order_by('-timestamp')  # Fetch all notifications
    context = {
        'notifications': notifications
    }
    return render(request, 'admin_dashboard/manage_notifications.html', context)


@login_required
@role_required(['admin'])
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    messages.success(request, "Notification deleted successfully.")
    return redirect('manage_notifications')  # Redirect back to the manage_notifications page







@role_required(['admin'])
def service_billing(request):
    search_query = request.GET.get('search', '')  # Capture the search query from the request

    if request.method == 'POST':
        # Handle Service Status Update
        billing_id = request.POST.get('billing_id')
        service_status = request.POST.get('service_status')

        billing = BillingDetails.objects.get(id=billing_id)
        billing.service_status = service_status
        billing.save()

        return redirect('service_billing')  # Refresh the page after update

    # Fetch all billing details and filter only by Ref No
    billing_details = BillingDetails.objects.all()
    if search_query:
        billing_details = billing_details.filter(ref_no__icontains=search_query)

    billing_details = billing_details.order_by('-id')

    # Add pagination
    paginator = Paginator(billing_details, 10)  # Show 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Calculate the serial number offset for infinite numbering
    serial_start = (page_obj.number - 1) * paginator.per_page

    return render(request, 'admin_dashboard/service_billing.html', {
        'billing_details': page_obj,  # Pass the paginated object
        'page_obj': page_obj,  # Include the paginator object for template rendering
        'serial_start': serial_start,
        'search_query': search_query,  # Pass the search query back to the template
    })






def update_service_status(request, billing_id):
    billing_details = get_object_or_404(BillingDetails, id=billing_id)
    if request.method == "POST":
        billing_details.service_status = request.POST.get("service_status")
        billing_details.save()
        return redirect("admin_service_billing")  # Admin's service billing page



@login_required
def view_billing_details(request, billing_id):
    billing_details = get_object_or_404(BillingDetails, id=billing_id)

    # Check user roles for access control
    if request.user.role not in ['admin', 'retailer', 'distributor']:
        raise PermissionDenied("You are not authorized to view this billing.")

    # Handle file upload for admins
    if request.user.role == 'admin' and request.method == 'POST':
        file = request.FILES.get('admin_completed_file')
        notes = request.POST.get('service_notes', '')

        if file:
            billing_details.admin_completed_file = file
            billing_details.service_notes = notes
            billing_details.service_status = 'Complete'  # Optional: Mark service as complete
            billing_details.save()
            messages.success(request, "Completed service file and notes uploaded successfully.")
        else:
            messages.error(request, "Please upload a valid file.")

        return redirect('admin_view_billing_details', billing_id=billing_id)

    return render(request, 'admin_dashboard/view_billing_details.html', {
        'billing_details': billing_details,
    })






# Delete Service
def delete_service_billing(request, billing_id):
    # Fetch the billing entry
    billing_entry = get_object_or_404(BillingDetails, id=billing_id)

    # Fetch the wallet associated with the user
    wallet = Wallet.objects.get(user=billing_entry.user)

    # Get the service price from the billing entry
    service_price = billing_entry.service.price

    # Add the service price back to the user's wallet
    wallet.balance += service_price
    wallet.save()

    # Log the transaction
    Transaction.objects.create(
        user=billing_entry.user,
        amount=service_price,
        transaction_type="Credit",
        balance_after_transaction=wallet.balance,
        description=f"Reversed Billing for {billing_entry.service.service_name}",
    )

    # Delete the billing entry
    billing_entry.delete()

    # Show a success message
    messages.success(request, "Service billing deleted, and amount refunded to the user's wallet.")
    return redirect('service_billing')  # Redirect to the admin dashboard or desired page









#Create a form where the admin can select a retailer and add money to their wallet.

User = get_user_model()

def add_or_deduct_money(request):
    if request.method == "POST":
        retailer_id = request.POST.get("retailer_id")
        action = request.POST.get("action")  # Either "add" or "deduct"
        amount = request.POST.get("amount")
        description = request.POST.get("description", "")

        # Validate and convert the amount to Decimal
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount. Please enter a valid number greater than zero.")
            return redirect("add_or_deduct_money")

        # Fetch the retailer and wallet
        try:
            retailer = User.objects.get(id=retailer_id)
            wallet, created = Wallet.objects.get_or_create(user=retailer)

            if action == "add":
                wallet.balance += amount
                transaction_type = "Credit"
                success_message = f"₹{amount} added to {retailer.get_full_name()}'s wallet successfully!"
            elif action == "deduct":
                # Ensure sufficient wallet balance
                if wallet.balance >= amount:
                    wallet.balance -= amount
                    transaction_type = "Debit"
                    success_message = f"₹{amount} deducted from {retailer.get_full_name()}'s wallet successfully!"
                else:
                    messages.error(request, "Insufficient wallet balance to complete the deduction.")
                    return redirect("add_or_deduct_money")
            else:
                messages.error(request, "Invalid action specified.")
                return redirect("add_or_deduct_money")

            # Save wallet changes
            wallet.save()

            # Log the transaction
            Transaction.objects.create(
                user=retailer,
                transaction_type=transaction_type,
                amount=amount,
                balance_after_transaction=wallet.balance,
                description=description,
            )

            messages.success(request, success_message)
        except User.DoesNotExist:
            messages.error(request, "Retailer not found!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect("view_transactions")

    # Fetch all users for the dropdown in the template
    users = User.objects.filter(is_staff=False)  # Adjust filters as needed
    return render(request, "admin_dashboard/add_money.html", {"users": users})







def admin_view_transactions(request):
    # Fetch transactions with service name and wallet balance
    transactions = Transaction.objects.select_related('user').values(
        'id',
        'user__full_name',
        'transaction_type',
        'amount',
        'balance_after_transaction',
        'description',
        'created_at',
    ).order_by('-created_at')

    # Apply search filter if provided
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(user__full_name__icontains=search_query) |
            # Q(service_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Calculate the serial number offset for infinite numbering
    serial_start = (page_obj.number - 1) * paginator.per_page
    

    context = {
        'transactions': page_obj,
        'search_query': search_query,
        'serial_start': serial_start,
    }
    return render(request, 'admin_dashboard/view_transactions.html', context)




@staff_member_required
def manage_access_requests(request):
    # Get the search query from the GET request
    search_query = request.GET.get('search', '')

    # Fetch all access requests and apply a search filter if the query exists
    access_requests_list = BankingPortalAccessRequest.objects.all().order_by('-created_at')
    if search_query:
        access_requests_list = access_requests_list.filter(
            Q(user__username__icontains=search_query) |  # Assuming you are filtering by username
            Q(user__email__icontains=search_query)  # Add other filters as needed
        )

    # Paginate the access requests
    paginator = Paginator(access_requests_list, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    access_requests = paginator.get_page(page_number)

    # Calculate the global starting index for the current page
    start_index = access_requests.start_index()

    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        access_request = get_object_or_404(BankingPortalAccessRequest, id=request_id)

        if action == 'activate':
            access_request.is_active = True
            access_request.save()
            messages.success(request, f"Access granted to {access_request.user.username}.")
        elif action == 'deactivate':
            access_request.is_active = False
            access_request.save()
            messages.warning(request, f"Access revoked for {access_request.user.username}.")

        return redirect('manage_access_requests')

    return render(request, 'admin_dashboard/manage_access_requests.html', {
        'access_requests': access_requests,
        'start_index': start_index,
        'search_query': search_query,  # Pass the search query to the template
    })


@login_required
@role_required(['admin'])
def change_demo_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        User = get_user_model()
        try:
            demo_user = User.objects.get(role='demo')
            demo_user.set_password(new_password)
            demo_user.save()
            messages.success(request, 'Demo user password changed successfully!')
        except User.DoesNotExist:
            messages.error(request, 'Demo user not found.')
    return redirect('admin_dashboard')



