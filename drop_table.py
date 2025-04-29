import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gst_dashboard.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS dashboard_equipmentorder;")
    print("Table dropped successfully") 