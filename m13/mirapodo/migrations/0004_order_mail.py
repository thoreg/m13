# Generated by Django 4.0.2 on 2022-09-30 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mirapodo", "0003_alter_orderitem_ean"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="mail",
            field=models.EmailField(
                default="mirapodo@msanufaktur13.de", max_length=254
            ),
            preserve_default=False,
        ),
    ]
