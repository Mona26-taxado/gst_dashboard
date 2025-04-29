from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from dashboard.utils import role_required, generate_qr
from django.contrib import messages
from dashboard.models import Notification, CustomUser, Equipment, EquipmentOrder, Service
from django.contrib.auth import logout
from dashboard.forms import UserUpdateForm
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta




def admin_dashboard(request):
    # Get current date
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get monthly sales for current month only if we're not in a future month/year
    monthly_sales = EquipmentOrder.objects.filter(
        status='paid',
        order_date__year=current_year,
        order_date__month=current_month,
        order_date__lte=current_date  # Ensure we don't get future dates
    ).aggregate(
        total_amount=Sum('total_amount'),
        total_base=Sum('base_price'),
        total_gst=Sum('gst_amount')
    )

    # Get total counts (excluding future dates)
    total_orders = EquipmentOrder.objects.filter(
        status='paid',
        order_date__lte=current_date
    ).count()
    
    total_amount = EquipmentOrder.objects.filter(
        status='paid',
        order_date__lte=current_date
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Get available years for the selector (only past and current year)
    available_years = (
        EquipmentOrder.objects
        .filter(
            status='paid',
            order_date__lte=current_date
        )
        .dates('order_date', 'year')
        .values_list('order_date__year', flat=True)
        .distinct()
        .order_by('-order_date__year')
    )

    # If no years available, add current year
    if not available_years:
        available_years = [current_year]

    context = {
        'total_orders': total_orders,
        'total_amount': total_amount,
        'monthly_sales': monthly_sales['total_amount'] or 0,
        'monthly_base': monthly_sales['total_base'] or 0,
        'monthly_gst': monthly_sales['total_gst'] or 0,
        'current_year': current_year,
        'available_years': available_years,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)




def login_view(request):
    error = None  # Initialize the error variable
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Log the user in if authentication succeeds
            return redirect("dashboard")  # Redirect to your post-login page
        else:
            error = "Invalid username or password!"  # Set error message if authentication fails
            print(f"Error: {error}")  # Debugging

    # Render login page with error message
    print(f"Rendering login page. Error: {error}")  # Debugging
    return render(request, "login.html", {"error": error})






@login_required
def role_based_redirect(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'retailer':
        return redirect('retailer_dashboard')
    elif user.role == 'distributor':
        return redirect('distributor_dashboard')
    elif user.role == 'master_distributor':
        return redirect('master_distributor_dashboard')
    else:
        return redirect('not_authorized')




def not_authorized_view(request):
    """
    View for the Access Denied page.
    """
    return render(request, 'not_authorized.html')






@login_required
def pin_entry(request):
    """
    View for validating PIN and redirecting to additional services.
    """
    if request.method == 'POST':
        entered_pin = request.POST.get('pin')  # Get the PIN entered by the user

        # Check if the entered PIN matches the user's PIN
        if request.user.pin == entered_pin:
            messages.success(request, 'PIN verified successfully.')
            return redirect('additional_services')  # Redirect to additional services

        # If the PIN doesn't match, show an error message
        messages.error(request, 'Invalid PIN. Please try again.')

    return render(request, 'dashboard/pin_entry.html')  # Render the PIN entry page




@login_required
@role_required(['retailer', 'distributor', 'master_distributor', 'admin'])  # Add roles allowed to access
def additional_services(request):
    """
    View for managing additional services.
    """
    return render(request, 'additional_services.html')



@login_required
def view_notifications(request):
    """
    View to display notifications for the logged-in user.
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'dashboard/view_notifications.html', {'notifications': notifications})



def custom_logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def account_settings(request):
    user = request.user  # Ensure user is authenticated

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('account_settings')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'account_settings.html', {'form': form})




from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse

class CustomPasswordChangeView(PasswordChangeView):
    def form_valid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form.save()
            return JsonResponse({'success': True})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        return super().form_invalid(form)








@role_required(['retailer', 'distributor'])
def generate_qr_for_recharge(request, user_id):
    try:
        distributor = CustomUser.objects.get(id=user_id)
        user_name = distributor.full_name

        # Generate the QR code
        qr_code_path = generate_qr(user_name)

        return render(request, 'recharge_wallet.html', {
            'user_name': user_name,
            'qr_code': qr_code_path,
            'user_id': user_id,  # Pass user_id for the form action
        })
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")




@login_required
def equipment_store(request):
    equipment_list = Equipment.objects.all()
    return render(request, 'equipment_store/equipment_store.html', {
        'equipment_list': equipment_list
    })




@login_required
def get_dashboard_data(request):
    """Get data for dashboard charts and statistics."""
    today = timezone.now()
    current_month = today.month
    current_year = today.year
    
    # Get monthly data
    monthly_data = EquipmentOrder.objects.filter(
            status='paid',
        order_date__year=current_year,
        order_date__month=current_month
    ).aggregate(
            total_amount=Sum('total_amount'),
        total_orders=Count('id')
    )

    # Get yearly data
    yearly_data = EquipmentOrder.objects.filter(
            status='paid',
        order_date__year=current_year
    ).aggregate(
        total_amount=Sum('total_amount'),
        total_orders=Count('id')
    )

    # Get monthly trend (last 6 months)
    months_data = []
    labels = []
    services_data = []
    bills_data = []
    
    for i in range(5, -1, -1):
        target_date = today - timedelta(days=i*30)
        month = target_date.month
        year = target_date.year
        
        # Count services for this month
        services_count = Service.objects.filter(
            billing_date__year=year,
            billing_date__month=month
        ).count()
        # Count bills for this month
        bills_count = EquipmentOrder.objects.filter(
            order_date__year=year,
            order_date__month=month,
            status='paid'
        ).count()
        
        month_name = target_date.strftime('%b-%Y')
        months_data.append(float(bills_count))  # Keep for backward compatibility if needed
        labels.append(month_name)
        services_data.append(services_count)
        bills_data.append(bills_count)

    return JsonResponse({
        'monthly': {
            'total_amount': float(monthly_data['total_amount'] or 0),
            'total_orders': monthly_data['total_orders'] or 0
            },
        'yearly': {
            'total_amount': float(yearly_data['total_amount'] or 0),
            'total_orders': yearly_data['total_orders'] or 0
        },
        'trend': {
            'labels': labels,
            'total_services': services_data,
            'total_bills': bills_data
        }
    })

@login_required
def get_monthly_income_data(request):
    today = timezone.now()
    labels = []
    centers_data = []
    bills_data = []

    for i in range(5, -1, -1):
        target_date = today - timedelta(days=i*30)
        month = target_date.month
        year = target_date.year

        # Count centers added this month
        centers_count = CustomUser.objects.filter(
            role='center',
            date_joined__year=year,
            date_joined__month=month
        ).count()

        # Count bills this month
        bills_count = EquipmentOrder.objects.filter(
            order_date__year=year,
            order_date__month=month,
            status='paid'
        ).count()

        month_name = target_date.strftime('%b-%Y')
        labels.append(month_name)
        centers_data.append(centers_count)
        bills_data.append(bills_count)

    return JsonResponse({
        'labels': labels,
        'total_centers': centers_data,
        'total_bills': bills_data,
    })