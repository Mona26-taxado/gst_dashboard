from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid
import random




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
    username = models.CharField(
        max_length=150, unique=True, null=True, blank=True, editable=False
    )  # Automatically generated
    branch_id = models.CharField(max_length=50, unique=True, null=True, blank=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    pin = models.CharField(max_length=4, blank=True, null=True, verbose_name="Security PIN")
    plain_text_password = models.CharField(max_length=128, blank=True, null=True)  # Temporary field
    full_name = models.CharField(max_length=255, blank=False, null=False)
    address = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
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
        ],
        null=True,
        blank=False,
    )
    
    referred_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals"
    )
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the user first
    # Ensure the user has a wallet
        if not hasattr(self, 'wallet'):
           Wallet.objects.create(user=self)


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
        choices=[('retailer', 'Retailer'), ('distributor', 'Distributor'), ('master_distributor', 'Master Distributor')],
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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customers")  # Fix here



    def __str__(self):
        return self.full_name





#Add a PIN field to the CustomUser model so that each user can have a unique PIN.
CustomUser = get_user_model()

class ServicePIN(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    pin = models.CharField(max_length=4, default="0000")  # 4-digit PIN

    def __str__(self):
        return f"PIN for {self.user.username}"





User = get_user_model()
class BillingDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Replace `1` with the correct default user ID
    ref_no = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Foreign Key to Customer
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Automatically delete related records
    billing_date = models.DateField(auto_now_add=True)
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

    def save(self, *args, **kwargs):
        if not self.ref_no:
            self.ref_no = f"REF-{random.randint(1000, 9999)}-{random.randint(1000000000, 9999999999)}"
        super().save(*args, **kwargs)









#To manage wallets and transactions, you need to create or update models for:

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.full_name} - Balance: {self.balance}"

    



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
        return f"{self.user.full_name} - {self.transaction_type} - {self.amount} - {self.balance_after}"

