# Generated by Django 4.0.2 on 2022-09-19 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mirapodo", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="orderitem",
            old_name="tb_id",
            new_name="position_item_id",
        ),
    ]
