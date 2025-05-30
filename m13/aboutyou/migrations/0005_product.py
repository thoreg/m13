# Generated by Django 5.1.7 on 2025-05-04 10:01

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aboutyou", "0004_remove_address_email_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                ("sku", models.CharField(max_length=32)),
                ("product_title", models.CharField(max_length=128)),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
    ]
