# Generated by Django 4.1.13 on 2024-12-23 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_alter_customuser_pin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='commission',
        ),
    ]
