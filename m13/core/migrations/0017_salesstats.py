# Generated by Django 5.1.5 on 2025-02-01 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_remove_price_zalando_marketplace_config"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalesStats",
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
                ("sku", models.CharField(max_length=32)),
                ("shipped", models.IntegerField()),
            ],
            options={
                "managed": False,
            },
        ),
    ]
