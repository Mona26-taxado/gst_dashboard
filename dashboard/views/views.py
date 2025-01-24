from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from dashboard.utils import role_required, generate_qr
from django.contrib import messages
from dashboard.models import Notification, CustomUser
from django.contrib.auth import logout
from dashboard.forms import UserUpdateForm
from django.http import HttpResponseForbidden, HttpResponse







def login_view(request):
    error = None  # Initialize the error variable
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in if authentication succeeds
            login(request, user)
            return redirect("dashboard")  # Redirect to your post-login page
        else:
            # Set error message if authentication fails
            error = "Invalid username or password!"
            print(f"Error set in view: {error}")  # Debugging

    # Render login page with error message
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