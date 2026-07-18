from django import forms
from dashboard.models import CustomUser, WhiteLabelTenant
from .models import Service, Customer, CSCService, CSCServiceDocument, CSCServiceRequest, Retailer2BillingDetails, BillingDetails
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify





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
        widgets = {
            'dob': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'wl-saas-input'},
            ),
            'start_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'wl-saas-input'},
            ),
        }

    def __init__(self, *args, **kwargs):
        self.allowed_roles = kwargs.pop(
            'allowed_roles',
            ['retailer', 'distributor', 'master_distributor', 'retailer_2', 'distributor_2'],
        )
        super().__init__(*args, **kwargs)
        # Ensure HTML5 date inputs accept the YYYY-MM-DD value
        for date_field in ('dob', 'start_date'):
            if date_field in self.fields:
                self.fields[date_field].input_formats = ['%Y-%m-%d']
        if self.instance and self.instance.pk:
            self.fields['plain_password'].initial = self.instance.plain_password
        if 'role' in self.fields:
            self.fields['role'].choices = [
                (value, label)
                for value, label in CustomUser._meta.get_field('role').choices
                if value in self.allowed_roles
            ]

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
        if role not in self.allowed_roles:
            raise forms.ValidationError("Invalid role selected.")
        return role


class WhiteLabelTenantForm(forms.ModelForm):
    class Meta:
        model = WhiteLabelTenant
        fields = [
            'name', 'slug', 'domain', 'logo', 'favicon',
            'primary_color', 'secondary_color', 'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'client-slug'}),
            'domain': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'portal.client.com'}
            ),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'favicon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control wl-color-input', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control wl-color-input', 'type': 'color'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_domain(self):
        domain = (self.cleaned_data.get('domain') or '').strip().lower()
        domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        if '/' in domain:
            raise forms.ValidationError("Enter host only, e.g. portal.client.com")
        return domain

    def clean_slug(self):
        slug = self.cleaned_data.get('slug') or ''
        if not slug and self.cleaned_data.get('name'):
            slug = slugify(self.cleaned_data['name'])
        return slug


class WhiteLabelAdminCreateForm(AddGSKForm):
    """Super Admin creates a white_label_admin linked to a tenant."""

    class Meta(AddGSKForm.Meta):
        fields = [
            'full_name', 'email', 'branch_id', 'mobile_number',
            'dob', 'address', 'state', 'city', 'start_date', 'plain_password',
        ]

    def __init__(self, *args, **kwargs):
        kwargs['allowed_roles'] = ['white_label_admin']
        super().__init__(*args, **kwargs)
        self.fields.pop('role', None)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'white_label_admin'
        if commit:
            user.save()
        return user



    




#Create a form for adding/editing services.
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["service_name", "price", "required_documents", "status"]
        help_texts = {
            "required_documents": "Retailers/distributors see this list on View services → View documents. Use one item per line or comma-separated values.",
        }
        widgets = {
            "service_name": forms.TextInput(
                attrs={"class": "form-control bg-dark text-white", "placeholder": "Service name"}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control bg-dark text-white", "step": "0.01", "placeholder": "Price"}
            ),
            "required_documents": forms.Textarea(
                attrs={
                    "class": "form-control bg-dark text-white",
                    "rows": 6,
                    "placeholder": "One document per line, or comma-separated (e.g. Aadhaar, PAN, Photo). Retailers see this on the Required documents page.",
                }
            ),
            "status": forms.Select(attrs={"class": "form-control bg-dark text-white"}),
        }




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


