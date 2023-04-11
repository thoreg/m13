# Generated by Django 4.0.2 on 2022-09-17 08:56

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("addition", models.CharField(blank=True, max_length=128, null=True)),
                ("city", models.CharField(max_length=128)),
                ("country_code", models.CharField(max_length=32)),
                ("first_name", models.CharField(max_length=128)),
                ("house_number", models.CharField(max_length=16)),
                ("last_name", models.CharField(max_length=128)),
                ("street", models.CharField(max_length=128)),
                ("title", models.CharField(blank=True, max_length=32, null=True)),
                ("zip_code", models.CharField(max_length=32)),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("marketplace_order_id", models.CharField(max_length=64)),
                ("order_date", models.DateTimeField()),
                (
                    "internal_status",
                    models.CharField(
                        choices=[
                            ("IMPORTED", "Imported"),
                            ("IN_PROGRESS", "In Progress"),
                            ("SHIPPED", "Shipped"),
                            ("FINISHED", "Finished"),
                            ("CANCELED", "Canceled"),
                        ],
                        default="IMPORTED",
                        max_length=11,
                    ),
                ),
                ("delivery_fee", models.CharField(max_length=32)),
                (
                    "delivery_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_address_set",
                        to="mirapodo.address",
                    ),
                ),
                (
                    "invoice_address",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="invoice_address_set",
                        to="mirapodo.address",
                    ),
                ),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, verbose_name="created"
                    ),
                ),
                (
                    "modified",
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, verbose_name="modified"
                    ),
                ),
                ("billing_text", models.CharField(max_length=32)),
                ("channel_id", models.CharField(max_length=2)),
                ("channeld_sku", models.CharField(max_length=32)),
                ("date_created", models.DateTimeField()),
                ("ean", models.CharField(max_length=13)),
                ("item_price", models.DecimalField(decimal_places=2, max_digits=5)),
                ("quantity", models.PositiveIntegerField()),
                ("sku", models.CharField(max_length=16)),
                ("tb_id", models.CharField(max_length=16)),
                ("transfer_price", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="mirapodo.order"
                    ),
                ),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
    ]
