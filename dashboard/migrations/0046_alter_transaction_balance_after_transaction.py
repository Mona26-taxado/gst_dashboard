# Generated by Django 5.1.4 on 2025-01-03 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0045_alter_transaction_balance_after_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='balance_after_transaction',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
