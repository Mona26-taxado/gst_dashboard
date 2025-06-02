from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from dashboard.utils import role_required, generate_qr
from django.contrib import messages
from dashboard.models import Notification, CustomUser, Equipment, EquipmentOrder, Service, Transaction, BillingDetails
from django.contrib.auth import logout
from dashboard.forms import UserUpdateForm
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
import string




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




def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(user, otp):
    from datetime import datetime
    subject = 'Your OTP for Grahak Sahaayata Kendra Login'
    html_message = f"""
    <div style='font-family: Arial, sans-serif; background: #181c24; padding: 30px;'>
      <div style='max-width: 500px; margin: auto;'>
        <div style='background: #232a36; border-radius: 16px; box-shadow: 0 2px 16px #10131a; padding: 0; overflow: hidden;'>
          <div style='background: #232a36; padding: 30px 30px 10px 30px; text-align: center;'>
            <h2 style='color: #4fd1c5; letter-spacing: 2px; margin-bottom: 0;'>Grahak Sahaayata Kendra</h2>
          </div>
          <div style='padding: 20px 30px 30px 30px;'>
            <p style='font-size: 16px; color: #e0e0e0; margin-top: 0;'>Dear {getattr(user, 'full_name', 'GSK')},</p>
            <p style='font-size: 16px; color: #e0e0e0;'>Your One Time Password (OTP) for login is:</p>
            <div style='display: flex; justify-content: center; margin: 30px 0;'>
              <div style='background: #181c24; border: 2px dashed #4fd1c5; border-radius: 12px; padding: 18px 40px; box-shadow: 0 2px 8px #10131a;'>
                <span style='font-size: 36px; letter-spacing: 10px; color: #4fd1c5; font-weight: bold;'>{otp}</span>
              </div>
            </div>
            <p style='font-size: 15px; color: #b0b0b0;'>This OTP is valid for <b>10 minutes</b>. Please do not share it with anyone.</p>
          </div>
          <div style='background: #181c24; padding: 16px; border-radius: 0 0 16px 16px;'>
            <p style='font-size: 13px; color: #555; text-align: center; margin: 0;'>&copy; {datetime.now().year} Grahak Sahaayata Kendra. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
    """
    from_email = 'GSK <' + settings.DEFAULT_FROM_EMAIL + '>'
    recipient_list = [user.email]
    send_mail(subject, '', from_email, recipient_list, html_message=html_message)

def otp_verification(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        try:
            otp_obj = OTP.objects.filter(user=request.user, is_verified=False).latest('created_at')
            if otp_obj.is_valid():
                if otp_obj.otp == entered_otp:
                    otp_obj.is_verified = True
                    otp_obj.save()
                    return redirect('role_based_redirect')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            else:
                messages.error(request, 'OTP has expired. Please request a new one.')
        except OTP.DoesNotExist:
            messages.error(request, 'No OTP found. Please request a new one.')
    
    return render(request, 'otp_verification.html')

def resend_otp(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Generate new OTP
    new_otp = generate_otp()
    
    # Save OTP to database
    OTP.objects.create(user=request.user, otp=new_otp)
    
    # Send OTP via email
    send_otp_email(request.user, new_otp)
    
    messages.success(request, 'New OTP has been sent to your email.')
    return redirect('otp_verification')

def demo_session_check(request):
    if request.user.role == 'demo':
        now = timezone.now().timestamp()
        if not request.session.get('demo_start'):
            request.session['demo_start'] = now
        elif now - request.session['demo_start'] > 20*60:
            # Change the demo user's password to a random value
            User = get_user_model()
            demo_user = User.objects.get(pk=request.user.pk)
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            demo_user.set_password(random_password)
            demo_user.save()
            logout(request)
            return redirect('login')
    return None

def custom_login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If demo user, reset demo_start
            if hasattr(user, 'role') and user.role == 'demo':
                now = timezone.now().timestamp()
                request.session['demo_start'] = now
            login(request, user)
            return redirect('redirect')  # or your dashboard URL
        else:
            error = "Invalid username or password. Please try again."
            print("DEBUG: Error set in view")  # Debug print
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
    elif user.role == 'demo':
        return redirect('dashboard_demo')
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
        
        month_name = target_date.strftime('%b %Y')
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
    new_retailers = []
    new_distributors = []
    wallet_credits = []
    total_billings = []

    # Get admin users (assuming role='admin')
    admin_users = CustomUser.objects.filter(role='admin').values_list('id', flat=True)

    for i in range(5, -1, -1):
        target_date = today - timedelta(days=i*30)
        month = target_date.month
        year = target_date.year

        # New Retailers
        retailers_count = CustomUser.objects.filter(
            role='retailer',
            date_joined__year=year,
            date_joined__month=month
        ).count()
        new_retailers.append(retailers_count)

        # New Distributors
        distributors_count = CustomUser.objects.filter(
            role='distributor',
            date_joined__year=year,
            date_joined__month=month
        ).count()
        new_distributors.append(distributors_count)

        # Wallet credits (all users)
        credits = Transaction.objects.filter(
            transaction_type='Credit',
            created_at__year=year,
            created_at__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
        wallet_credits.append(float(credits))

        # Total billings
        billings = BillingDetails.objects.filter(
            billing_date__year=year,
            billing_date__month=month
        ).count()
        total_billings.append(billings)

        labels.append(target_date.strftime('%b %Y'))

    return JsonResponse({
        'labels': labels,
        'new_retailers': new_retailers,
        'new_distributors': new_distributors,
        'wallet_credits': wallet_credits,
        'total_billings': total_billings,
        'this_month': {
            'new_retailers': new_retailers[-1],
            'new_distributors': new_distributors[-1],
            'wallet_credits': wallet_credits[-1],
            'total_billings': total_billings[-1],
        }
    })

@login_required
def dashboard(request):
    user = request.user
    # Demo session expiry check
    demo_expiry = demo_session_check(request)
    if demo_expiry:
        return demo_expiry
    if user.role == 'retailer':
        return redirect('retailer_dashboard')
    elif user.role == 'distributor':
        return redirect('distributor_dashboard')
    elif user.role == 'master_distributor':
        return redirect('master_distributor_dashboard')
    elif user.role == 'demo':
        from dashboard.models import BillingDetails, Service, Transaction, Notification
        total_services = Service.objects.count()
        total_billings = BillingDetails.objects.count()
        wallet_balance = 0  # Set to 0 or a demo value
        billing_details = BillingDetails.objects.all()[:5]
        notifications = Notification.objects.all()[:5]
        # Dummy data for charts
        demo_bar_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        demo_bar_data = [12, 19, 3, 5, 2, 3]
        demo_doughnut_labels = ['Total Services', 'Total Billings']
        demo_doughnut_data = [25, 15]
        context = {
            'total_services': total_services,
            'total_billings': total_billings,
            'wallet_balance': wallet_balance,
            'billing_details': billing_details,
            'notifications': notifications,
            'demo_bar_labels': demo_bar_labels,
            'demo_bar_data': demo_bar_data,
            'demo_doughnut_labels': demo_doughnut_labels,
            'demo_doughnut_data': demo_doughnut_data,
        }
        return render(request, 'dashboard_demo.html', context)
    else:
        return render(request, 'not_authorized.html')

# Example: Block form submissions for demo users
def some_form_view(request):
    if request.user.role == 'demo' and request.method == 'POST':
        return HttpResponseForbidden('Demo users cannot submit forms.')
    # ... rest of your form logic ...

# Example: Block add user for demo users
def add_user_view(request):
    if request.user.role == 'demo':
        return HttpResponseForbidden('Demo users cannot add users.')
    # ... rest of your add user logic ...

@login_required
def additional_services_demo(request):
    if request.user.role != 'demo':
        return render(request, 'not_authorized.html')
    return render(request, 'demo_pages/additional_services_demo.html')

@login_required
def equipments_store_demo(request):
    if request.user.role != 'demo':
        return render(request, 'not_authorized.html')
    return render(request, 'demo_pages/equipments_store_demo.html')

@login_required
def total_services_demo(request):
    if request.user.role != 'demo':
        return render(request, 'not_authorized.html')
    services_list = Service.objects.all().order_by('service_name')  # Order alphabetically by name
    paginator = Paginator(services_list, 10)  # Show 10 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_index = page_obj.start_index()
    return render(
        request,
        'demo_pages/total_services_demo.html',
        {'page_obj': page_obj, 'start_index': start_index}
    )

@login_required
def dummy_page(request):
    if request.user.role != 'demo':
        return render(request, 'not_authorized.html')
    return render(request, 'demo_pages/dummy_page.html')


@role_required(['retailer', 'distributor', 'master_distributor'])
@login_required
def recharge_plans_view(request):
    """
    View to display available recharge plans to the retailer, distributor, and master distributor.
    """
    return render(request, 'recharge_plans.html')