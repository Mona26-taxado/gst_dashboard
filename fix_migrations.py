import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Delete the problematic migration record
    cursor.execute("DELETE FROM django_migrations WHERE app='dashboard' AND name='0003_equipmentorder';")
    cursor.execute("DELETE FROM django_migrations WHERE app='dashboard' AND name='0002_equipment';")
    print("Migration records removed successfully") 