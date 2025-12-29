from django import forms
from dashboard.models import CustomUser
from .models import Service, Customer, CSCService, CSCServiceDocument, CSCServiceRequest, Retailer2BillingDetails, BillingDetails
from django.contrib.auth.hashers import make_password





class AddGSKForm(forms.ModelForm):
    plain_password = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter password'}),
        required=False,
        label="Password",
        help_text="The password will be shown in plain text for editing purposes.",
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'role', 'branch_id', 'mobile_number', 'dob', 'address', 'state', 'city', 'start_date', 'plain_password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['plain_password'].initial = self.instance.plain_password

    def save(self, commit=True):
        user = super().save(commit=False)
        plain_password = self.cleaned_data.get('plain_password')
        if plain_password:
            user.set_password(plain_password)  # Save hashed password
            user.plain_password = plain_password  # Save plain text password
        if commit:
            user.save()
        return user




    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['retailer', 'distributor', 'master_distributor', 'retailer_2', 'distributor_2']:
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

# CSC 2.0 Forms
class CSCServiceForm(forms.ModelForm):
    class Meta:
        model = CSCService
        fields = ['service_name', 'description', 'price', 'wallet_deduction', 'required_documents', 'service_icon', 'service_color', 'service_image', 'external_link', 'is_active']
        widgets = {
            'service_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'wallet_deduction': forms.NumberInput(attrs={'class': 'form-control'}),
            'required_documents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'service_icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'mdi mdi-account'}),
            'service_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'service_image': forms.FileInput(attrs={'class': 'form-control'}),
            'external_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CSCServiceDocumentForm(forms.ModelForm):
    class Meta:
        model = CSCServiceDocument
        fields = ['document_name', 'is_required', 'description']
        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']


        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']


        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']


        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']


        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class CSCServiceRequestForm(forms.ModelForm):
    class Meta:
        model = CSCServiceRequest
        fields = ['service', 'customer_name', 'customer_mobile', 'notes']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Old Billing Forms (for non-Retailer 2.0 users)
class BillingDetailsForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']

# Retailer 2.0 Billing Form
class Retailer2BillingForm(forms.ModelForm):
    class Meta:
        model = Retailer2BillingDetails
        exclude = ['user', 'ref_no', 'invoice_id', 'billing_date', 'admin_completed_file']


