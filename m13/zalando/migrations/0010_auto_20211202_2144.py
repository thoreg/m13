# Generated by Django 3.2.9 on 2021-12-02 20:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zalando", "0009_statsorderitems"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderitem",
            name="orig_created_timestamp",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="orig_modified_timestamp",
            field=models.DateTimeField(null=True),
        ),
    ]
