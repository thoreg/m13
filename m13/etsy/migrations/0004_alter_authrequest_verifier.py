# Generated by Django 3.2.8 on 2021-10-24 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy', '0003_alter_authrequest_code_challenge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authrequest',
            name='verifier',
            field=models.CharField(max_length=128),
        ),
    ]
