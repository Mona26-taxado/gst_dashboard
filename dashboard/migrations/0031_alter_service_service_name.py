# Generated by Django 4.1.13 on 2024-12-27 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_alter_wallet_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='service_name',
            field=models.CharField(max_length=255),
        ),
    ]
