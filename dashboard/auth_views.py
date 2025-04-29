from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.shortcuts import render
from .models import Equipment

class ForgotPasswordView(PasswordResetView):
    template_name = 'auth/forgot_password.html'
    email_template_name = 'auth/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm





def equipment_store(request):
    items = Equipment.objects.filter(stock__gt=0)
    return render(request, 'equipment_store/equipment_store.html', {
        'equipment_list': items
    })
