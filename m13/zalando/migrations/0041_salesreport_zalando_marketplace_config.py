# Generated by Django 5.0 on 2024-01-20 12:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_remove_price_zalando_marketplace_config"),
        ("zalando", "0040_alter_salesreport_import_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="salesreport",
            name="zalando_marketplace_config",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.marketplaceconfig",
            ),
        ),
    ]
