# Generated by Django 3.2.8 on 2021-10-31 20:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("etsy", "0009_auto_20211031_2111"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="article_number",
        ),
    ]
