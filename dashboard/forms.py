from django import forms
from dashboard.models import CustomUser
from .models import Service
from .models import Customer
from django.contrib.auth.hashers import make_password
from .models import BillingDetails





class AddGSKForm(forms.ModelForm):
    plain_text_password = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter password'}),  # Use TextInput for plain text
        required=True,
        label="Password"
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'role', 'branch_id', 'mobile_number', 'dob', 'address', 'state', 'city', 'start_date']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['plain_text_password'])  # Hash and save the password
        if commit:
            user.save()
        return user

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['retailer', 'distributor', 'master_distributor']:
            raise forms.ValidationError("Invalid role selected.")
        return role







#Create a form for adding/editing services.
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'price',  'status']




class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'date_of_birth', 'dob', 'address', 'email', 'mobile', 'state', 'city', 'gender', 'pin_code']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }



class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        fields = [
            'customer', 'service', 'payment_mode', 
            'payment_status', 'service_status', 'id_proof', 
            'address_proof', 'pan_card', 'banking', 
            'photo', 'others', 'service_notes'
        ]
        widgets = {
            'ref_no': forms.TextInput(attrs={'readonly': 'readonly'}),
            'billing_date': forms.DateInput(attrs={'readonly': 'readonly'}),
        }





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'mobile_number', 'address', 'profile_photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        # In the form
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if user is not None and user.is_staff:
            self.fields.pop('email')

