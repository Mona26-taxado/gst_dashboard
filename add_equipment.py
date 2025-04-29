import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from dashboard.models import Equipment

# Sample equipment data
equipment_data = [
    {
        'name': 'High-Speed Thermal Printer',
        'description': 'Professional thermal printer with auto-cutter, USB & LAN ports. Perfect for high-volume receipt printing.',
        'price': 8999,
        'stock': 15,
        'category': 'printers'
    },
    {
        'name': 'Mantra L1 Fingerprint Scanner',
        'description': 'UIDAI certified fingerprint scanner for Aadhaar authentication. High-quality optical sensor with 500 DPI resolution.',
        'price': 2999,
        'stock': 20,
        'category': 'biometric'
    },
    {
        'name': 'Complete Desktop System',
        'description': 'Full desktop setup including CPU, monitor, keyboard, and mouse. Intel Core i3, 8GB RAM, 256GB SSD.',
        'price': 35999,
        'stock': 5,
        'category': 'computers'
    }
]

# Add equipment to database
for item in equipment_data:
    Equipment.objects.create(**item)
    print(f"Added {item['name']}") 