from django.core.management.base import BaseCommand
from dashboard.models import Equipment

class Command(BaseCommand):
    help = 'Add sample equipment data'

    def handle(self, *args, **kwargs):
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

        for item in equipment_data:
            Equipment.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"Added {item['name']}")) 