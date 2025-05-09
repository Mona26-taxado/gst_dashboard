# Generated by Django 4.2.11 on 2025-04-30 16:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0074_add_equipment_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingdetails',
            name='invoice_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=255, unique=True)),
                ('customer_name', models.CharField(max_length=255)),
                ('service_name', models.CharField(max_length=255)),
                ('original_service_charge', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice_date', models.DateTimeField()),
                ('billing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.billingdetails')),
                ('retailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
