# Generated by Django 4.1.5 on 2023-03-14 09:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("etsy", "0015_orderitem_quantity"),
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
                ],
                default="OPEN",
                max_length=18,
            ),
        ),
    ]
