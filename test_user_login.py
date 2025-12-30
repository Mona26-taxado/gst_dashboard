#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from django.contrib.auth import authenticate
from dashboard.models import CustomUser

# Test user authentication
email = "naveeng123gupta@gmail.com"
password = "your_password_here"  # Replace with actual password

print(f"Testing authentication for: {email}")

user = authenticate(username=email, password=password)

if user:
    print(f"✅ Authentication successful!")
    print(f"User: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
else:
    print(f"❌ Authentication failed!")
    print("Please check the password.")

# Also check if user exists
try:
    user_obj = CustomUser.objects.get(email=email)
    print(f"\nUser exists in database:")
    print(f"Email: {user_obj.email}")
    print(f"Full Name: {user_obj.full_name}")
    print(f"Role: {user_obj.role}")
    print(f"Active: {user_obj.is_active}")
    print(f"Has password: {user_obj.has_usable_password()}")
except CustomUser.DoesNotExist:
    print(f"\n❌ User not found in database!") 