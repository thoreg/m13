# Generated by Django 3.2.8 on 2021-11-02 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("etsy", "0011_auto_20211102_0741"),
    ]

    operations = [
        migrations.RenameField(
            model_name="authtoken",
            old_name="auth_token",
            new_name="token",
        ),
    ]
