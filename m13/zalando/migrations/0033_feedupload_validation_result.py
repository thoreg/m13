# Generated by Django 4.2.5 on 2023-11-13 16:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zalando", "0032_rawdailyshipmentreport_marketplace_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedupload",
            name="validation_result",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
    ]
