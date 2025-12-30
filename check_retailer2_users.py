#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CustomUser

# Check for Retailer 2.0 users
retailer2_users = CustomUser.objects.filter(role='retailer_2')
distributor2_users = CustomUser.objects.filter(role='distributor_2')

print("=== Retailer 2.0 Users ===")
for user in retailer2_users:
    print(f"Email: {user.email}")
    print(f"Full Name: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print("---")

print("\n=== Distributor 2.0 Users ===")
for user in distributor2_users:
    print(f"Email: {user.email}")
    print(f"Full Name: {user.full_name}")
    print(f"Role: {user.role}")
    print(f"Active: {user.is_active}")
    print("---")

print(f"\nTotal Retailer 2.0 users: {retailer2_users.count()}")
print(f"Total Distributor 2.0 users: {distributor2_users.count()}") 