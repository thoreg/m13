# Generated by Django 4.1.5 on 2023-07-11 03:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("etsy", "0017_remove_order_marketplace_order_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("COMPLETED", "Completed"),
                    ("OPEN", "Open"),
                    ("PAID", "Paid"),
                    ("PAYMENT_PROCESSING", "Payment Processing"),
                    ("CANCELED", "Canceled"),
                    ("PARTIALLY_REFUNDED", "Partially Refunded"),
                ],
                default="OPEN",
                max_length=18,
            ),
        ),
    ]
