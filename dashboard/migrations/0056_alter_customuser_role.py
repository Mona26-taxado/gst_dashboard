# Generated by Django 5.1.4 on 2025-01-08 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0055_customuser_plain_text_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('retailer', 'Retailer'), ('distributor', 'Distributor'), ('master_distributor', 'Master Distributor')], default='retailer', max_length=50, null=True),
        ),
    ]
