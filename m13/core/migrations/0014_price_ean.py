# Generated by Django 5.0 on 2024-01-18 05:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_price_pimped_zalando"),
    ]

    operations = [
        migrations.AddField(
            model_name="price",
            name="ean",
            field=models.CharField(blank=True, max_length=13, null=True, unique=True),
        ),
    ]
