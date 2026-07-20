from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0094_merge_20260716_1737"),
    ]

    operations = [
        migrations.AddField(
            model_name="whitelabeltenant",
            name="wallet_upi_id",
            field=models.CharField(
                blank=True,
                default="",
                help_text="UPI ID for wallet recharge of this white-label network",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="whitelabeltenant",
            name="wallet_qr_code",
            field=models.ImageField(
                blank=True,
                help_text="QR code image for wallet recharge of this white-label network",
                null=True,
                upload_to="white_label/wallet_qr/",
            ),
        ),
    ]
