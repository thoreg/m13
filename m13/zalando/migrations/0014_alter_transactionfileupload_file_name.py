# Generated by Django 4.0.2 on 2022-05-16 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0013_remove_transactionfileupload_month_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionfileupload',
            name='file_name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
