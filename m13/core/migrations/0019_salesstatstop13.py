# Generated by Django 5.1.5 on 2025-02-01 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_delete_salesstats"),
    ]

    operations = [
        migrations.CreateModel(
            name="SalesStatsTop13",
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
            ],
            options={
                "db_table": "core_salesstats_top13",
                "managed": False,
            },
        ),
    ]
