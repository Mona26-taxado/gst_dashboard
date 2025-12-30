from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid
import random
from django.utils import timezone
from django.utils.timezone import now  # Add this import
from decimal import Decimal





# Create your models here.

class ServiceRequest(models.Model):
    customer_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50)
    request_date = models.DateTimeField(auto_now_add=True)


# Role Based Access



class CustomUser(AbstractUser):
    # Use email as the login identifier
    email = models.EmailField(unique=True, null=False, blank=False)
    is_retailer = models.BooleanField(default=False)
    is_distributor = models.BooleanField(default=False)  # New field for distributor role
    username = models.CharField(
        max_length=150, unique=True, null=True, blank=True, editable=False
    )  # Automatically generated
    branch_id = models.CharField(max_length=50, unique=True, null=True, blank=False)
    plain_text_password = models.CharField(max_length=128, null=True, blank=True)  # For storing plain text password
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    pin = models.CharField(max_length=4, blank=True, null=True, verbose_name="Security PIN")
    full_name = models.CharField(max_length=255, blank=False, null=False)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set at creation time
    plain_password = models.CharField(max_length=128, null=True, blank=True)  # Add this field
    current_gsk_count = models.IntegerField(default=0)
    gender = models.CharField(
        max_length=10, choices=[("Male", "Male"), ("Female", "Female")], null=True, blank=True
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("admin", "Admin"),
            ("retailer", "Retailer"),
            ("distributor", "Distributor"),
            ("master_distributor", "Master Distributor"),
            ("retailer_2", "Retailer 2.0"),
            ("distributor_2", "Distributor 2.0"),
        ],
        null=True,
        blank=False,
        default='retailer'  # Default role
    )
    
    referred_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals"
    )
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the user first
    # Ensure the user has a wallet
        if not hasattr(self, 'wallet'):
           Wallet.objects.create(user=self)

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.plain_password = raw_password

    def save(self, *args, **kwargs):
        print("DEBUG: Saving User:", self)  # Log user being saved
        super().save(*args, **kwargs)




    def __str__(self):
        return self.email


    



class UserRole(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=20)


class GSK(models.Model):
    branch_name = models.CharField(max_length=255)
    branch_id = models.CharField(max_length=20)
    branch_type = models.CharField(max_length=50, choices=[('Retailer', 'Retailer'), ('Distributor', 'Distributor'), ('Master Distributor', 'Master Distributor')])
    start_date = models.DateField()
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    address = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    


# Ensure your model for services has fields such as service_name, price, commission, status, and created_by (if you want to track which user created the service).


class Service(models.Model):
    service_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    required_documents = models.TextField(blank=True, null=True)
    billing_date = models.DateTimeField(auto_now_add=True)  # Ensure this field exists

    # Add the status field if it does not exist
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')


    def service_charge(self):
        # Calculate service charge dynamically based on the price
        return (self.price * self.service_charge_percentage) / 100

    def __str__(self):
        return self.service_name
    



#Add a Notification model to store notifications in your database. This model will include fields such as title, message, receiver, and status.

CustomUser = get_user_model()


class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True  # Allow null for broadcast notifications
    )
    group = models.CharField(
        max_length=50,
        choices=[('retailer', 'Retailer'), ('distributor', 'Distributor'), ('master_distributor', 'Master Distributor'), ('retailer_2', 'Retailer 2.0'), ('distributor_2', 'Distributor 2.0')],
        null=True,
        blank=True  # Allow blank for individual notifications
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Notification for {self.user.username}"
        elif self.group:
            return f"Notification for {self.group.capitalize()} Group"
        return "Broadcast Notification"




User = get_user_model()
class Customer(models.Model):

    full_name = models.CharField(max_length=255, default="Unknown")
    date_of_birth = models.DateField(null=True, blank=True)  # Add Date of Birth
    address = models.TextField()
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=15, null=True, blank=True)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    pin_code = models.CharField(max_length=6, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="customers")
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    current_gsk_count = models.IntegerField(default=0)  # Default value for current_gsk_count


    def __str__(self):
        return self.full_name


class ServicePIN(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    pin = models.CharField(max_length=4, default="0000")  # 4-digit PIN

    def __str__(self):
        return f"PIN for {self.user.email}"


class BillingDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Replace `1` with the correct default user ID
    ref_no = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Foreign Key to Customer
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Automatically delete related records
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add amount field
    billing_date = models.DateTimeField(auto_now_add=True, null=True)  # Ensure this field is defined
    payment_mode = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Online', 'Online')])
    payment_status = models.CharField(max_length=50, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    address_proof = models.FileField(upload_to='address_proofs/', blank=True, null=True)
    pan_card = models.CharField(max_length=255, null=True, blank=True)
    banking = models.FileField(upload_to='banking/', null=True, blank=True)
    photo = models.FileField(upload_to='photos/', null=True, blank=True)
    others = models.FileField(upload_to='others/', null=True, blank=True)
    service_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Complete', 'Complete')],
        default='Pending',
    )
    service_notes = models.TextField(null=True, blank=True)
    admin_completed_file = models.FileField(upload_to='completed_service_files/', null=True, blank=True)
    invoice_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Add this field

    def save(self, *args, **kwargs):
        if not self.ref_no:
            # Generate a unique reference number
            import uuid
            self.ref_no = f"BILL-{uuid.uuid4().hex[:8].upper()}"
        # Set amount from service price if not set
        if not self.amount and self.service:
            self.amount = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Billing {self.ref_no} - {self.customer.full_name}"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet for {self.user.email}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("Credit", "Credit"),
        ("Debit", "Debit"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} for {self.user.email}"


class BankingPortalAccessRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests')
    is_active = models.BooleanField(default=False)
    request_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=now)  # Sets the current timestamp as the default

    def __str__(self):
        return f"Banking Portal Access Request for {self.user.email}"


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='equipment_images/', null=True, blank=True)

    class Meta:
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'

    def __str__(self):
        return self.name


class EquipmentOrder(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, null=True, blank=True)  # Make nullable temporarily
    quantity = models.IntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Equipment Order'
        verbose_name_plural = 'Equipment Orders'

    def __str__(self):
        return f"Order {self.id} - {self.equipment.name}"

    def save(self, *args, **kwargs):
        # Calculate GST and total amount
        self.base_price = self.equipment.price * self.quantity
        self.gst_amount = self.base_price * Decimal('0.18')  # 18% GST
        self.total_amount = self.base_price + self.gst_amount
        super().save(*args, **kwargs)


class Invoice(models.Model):
    billing = models.ForeignKey('BillingDetails', on_delete=models.CASCADE)
    retailer = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=255, unique=True)
    customer_name = models.CharField(max_length=255)
    service_name = models.CharField(max_length=255)
    original_service_charge = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_date = models.DateTimeField()

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class CSCService(models.Model):
    """Model for CSC 2.0 services that can be customized by admin"""
    service_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    required_documents = models.TextField(help_text="List of required documents separated by commas")
    service_icon = models.CharField(max_length=100, default="mdi mdi-cog", help_text="Material Design Icon class (e.g., mdi mdi-account)")
    service_color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code for service card")
    service_image = models.ImageField(upload_to='csc_services/', blank=True, null=True, help_text="Service card image")
    external_link = models.URLField(blank=True, null=True, help_text="External link for the service (optional)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CSC Service'
        verbose_name_plural = 'CSC Services'

    def __str__(self):
        return self.service_name


class CSCServiceDocument(models.Model):
    """Model for managing required documents for CSC services"""
    service = models.ForeignKey(CSCService, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=100)
    is_required = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'CSC Service Document'
        verbose_name_plural = 'CSC Service Documents'

    def __str__(self):
        return f"{self.document_name} for {self.service.service_name}"


class CSCServiceRequest(models.Model):
    """Model for tracking CSC service requests from Retailer 2.0 users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service = models.ForeignKey(CSCService, on_delete=models.CASCADE)
    retailer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'retailer_2'})
    customer_name = models.CharField(max_length=200)
    customer_mobile = models.CharField(max_length=15)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_deduction = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    documents_uploaded = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CSC Service Request'
        verbose_name_plural = 'CSC Service Requests'

    def __str__(self):
        return f"{self.service.service_name} request by {self.retailer.full_name}"


class Retailer2BillingDetails(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ref_no = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(CSCService, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add amount field
    billing_date = models.DateTimeField(auto_now_add=True, null=True)
    payment_mode = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Online', 'Online')])
    payment_status = models.CharField(max_length=50, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')
    id_proof = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    address_proof = models.FileField(upload_to='address_proofs/', blank=True, null=True)
    pan_card = models.CharField(max_length=255, null=True, blank=True)
    banking = models.FileField(upload_to='banking/', null=True, blank=True)
    photo = models.FileField(upload_to='photos/', null=True, blank=True)
    others = models.FileField(upload_to='others/', null=True, blank=True)
    service_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Complete', 'Complete')],
        default='Pending',
    )
    service_notes = models.TextField(null=True, blank=True)
    admin_completed_file = models.FileField(upload_to='completed_service_files/', null=True, blank=True)
    invoice_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ref_no:
            # Generate a unique reference number
            import uuid
            self.ref_no = f"R2-BILL-{uuid.uuid4().hex[:8].upper()}"
        # Set amount from service price if not set
        if not self.amount and self.service:
            self.amount = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Retailer 2.0 Billing {self.ref_no} - {self.customer.full_name}"



