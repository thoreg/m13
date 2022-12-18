# Generated by Django 4.0.2 on 2022-05-03 04:28

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zalando", "0011_statsorderitem_view_update"),
    ]

    operations = [
        migrations.CreateModel(
            name="TransactionFileUpload",
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
                ("status_code_upload", models.BooleanField(default=False)),
                ("status_code_processing", models.BooleanField(default=False)),
                ("original_csv", models.FileField(upload_to="zalando/finance/")),
                ("month", models.IntegerField()),
            ],
            options={
                "get_latest_by": "modified",
                "abstract": False,
            },
        ),
    ]
