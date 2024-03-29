# Generated by Django 3.2.6 on 2021-09-20 16:22

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zalando", "0006_auto_20210916_0552"),
    ]

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
                ("line", models.CharField(blank=True, max_length=128, null=True)),
                ("city", models.CharField(max_length=128)),
                ("country_code", models.CharField(max_length=32)),
                ("first_name", models.CharField(max_length=128)),
                ("house_number", models.CharField(max_length=16)),
                ("last_name", models.CharField(max_length=128)),
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
                ("marketplace_order_number", models.CharField(max_length=32)),
                ("order_date", models.DateTimeField()),
                ("last_modified_date", models.DateTimeField()),
                ("store_id", models.CharField(max_length=8)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ASSIGNED", "Assigned"),
                            ("FULFILLED", "Fulfilled"),
                            ("ROUTED", "Routed"),
                            ("CANCELLED", "Cancelled"),
                            ("RETURNED", "Returned"),
                        ],
                        default="ASSIGNED",
                        max_length=11,
                    ),
                ),
                (
                    "delivery_address",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_address_set",
                        to="zalando.address",
                    ),
                ),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="oeawebhookmessage",
            name="processed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Shipment",
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
                ("carrier", models.CharField(max_length=128)),
                ("tracking_info", models.CharField(max_length=256)),
                ("response_status_code", models.PositiveSmallIntegerField()),
                ("response", models.JSONField()),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="zalando.order"
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
                ("cancellation_date", models.DateTimeField(blank=True, null=True)),
                ("fulfillment_status", models.CharField(max_length=32)),
                ("price_in_cent", models.PositiveIntegerField()),
                ("currency", models.CharField(max_length=8)),
                ("position_item_id", models.CharField(max_length=36)),
                ("article_number", models.CharField(max_length=36)),
                ("ean", models.CharField(max_length=16)),
                ("carrier", models.CharField(blank=True, max_length=32, null=True)),
                (
                    "tracking_number",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="zalando.order"
                    ),
                ),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
    ]
