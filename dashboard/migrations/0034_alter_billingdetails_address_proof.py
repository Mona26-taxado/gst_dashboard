# Generated by Django 4.1.13 on 2024-12-28 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_alter_billingdetails_id_proof'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingdetails',
            name='address_proof',
            field=models.FileField(blank=True, null=True, upload_to='address_proofs/'),
        ),
    ]
