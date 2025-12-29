#!/usr/bin/env python
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 
"""
Script to upload sample images to existing CSC services
Run this script to add sample images to CSC services for testing
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import CSCService
from django.core.files import File
from django.conf import settings

def upload_sample_images():
    """Upload sample images to CSC services"""
    
    # Sample image mappings for CSC services with correct paths
    sample_images = {
        'Digital PAN Card': 'dashboard/static/assets/images/online-pan-service-center.png',
        'Aadhar Update': 'dashboard/static/assets/images/png-transparent-aadhaar-hd-logo-removebg-preview.png',
        'Passport Application': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Registration': 'dashboard/static/assets/images/vh.png',
        'Driving License': 'dashboard/static/assets/images/customer-service.png',
        'Birth Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Income Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Caste Certificate': 'dashboard/static/assets/images/customer-service.png',
        'Voter ID Card': 'dashboard/static/assets/images/vh.png',
        'GST Registration': 'dashboard/static/assets/images/customer-service.png',
    }
    
    print("Uploading sample images to CSC services...")
    
    for service_name, image_path in sample_images.items():
        try:
            service = CSCService.objects.get(service_name=service_name)
            
            # Check if image already exists
            if service.service_image:
                print(f"✓ {service_name} already has an image")
                continue
                
            # Check if source image exists
            if not os.path.exists(image_path):
                print(f"✗ Source image not found: {image_path}")
                continue
                
            # Upload the image
            with open(image_path, 'rb') as f:
                service.service_image.save(
                    os.path.basename(image_path),
                    File(f),
                    save=True
                )
            print(f"✓ Uploaded image for {service_name}")
            
        except CSCService.DoesNotExist:
            print(f"✗ Service not found: {service_name}")
        except Exception as e:
            print(f"✗ Error uploading image for {service_name}: {e}")
    
    print("\nSample image upload completed!")
    print("\nTo view the images:")
    print("1. Go to Django Admin: http://127.0.0.1:8000/admin/")
    print("2. Navigate to Dashboard > CSC Services")
    print("3. Check that images are uploaded")
    print("4. Visit Retailer 2.0 Dashboard to see the images")

if __name__ == '__main__':
    upload_sample_images() 