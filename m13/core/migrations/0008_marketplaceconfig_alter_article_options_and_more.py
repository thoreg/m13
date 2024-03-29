# Generated by Django 4.1.5 on 2023-02-17 12:11

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_price"),
    ]

    operations = [
        migrations.CreateModel(
            name="MarketplaceConfig",
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
                (
                    "name",
                    models.CharField(
                        choices=[("OTTO", "Otto"), ("ZALANDO", "Zalando")],
                        default="OTTO",
                        max_length=16,
                    ),
                ),
                ("shipping_costs", models.DecimalField(decimal_places=2, max_digits=5)),
                ("return_costs", models.DecimalField(decimal_places=2, max_digits=5)),
                ("provision_in_percent", models.IntegerField(blank=True, null=True)),
                ("vat_in_percent", models.IntegerField(default=19)),
                ("generic_costs_in_percent", models.IntegerField(default=19)),
                ("active", models.BooleanField()),
            ],
            options={
                "verbose_name_plural": "Marketplace Configurations",
            },
        ),
        migrations.AlterModelOptions(
            name="article",
            options={"get_latest_by": "modified"},
        ),
        migrations.RenameField(
            model_name="price",
            old_name="article",
            new_name="sku",
        ),
        migrations.RemoveField(
            model_name="price",
            name="o_return_costs",
        ),
        migrations.RemoveField(
            model_name="price",
            name="o_shipping_costs",
        ),
        migrations.RemoveField(
            model_name="price",
            name="z_return_costs",
        ),
        migrations.RemoveField(
            model_name="price",
            name="z_shipping_costs",
        ),
    ]
