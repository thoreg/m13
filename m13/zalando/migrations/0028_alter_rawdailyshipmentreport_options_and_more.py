# Generated by Django 4.0.2 on 2022-07-15 04:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0027_remove_rawdailyshipmentreport_article_number_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rawdailyshipmentreport',
            options={},
        ),
        migrations.AlterModelOptions(
            name='transactionfileupload',
            options={},
        ),
        migrations.AlterModelTable(
            name='rawdailyshipmentreport',
            table='zalando_dailyshipmentreport_raw',
        ),
        migrations.AlterModelTable(
            name='transactionfileupload',
            table='zalando_dailyshipmentreport_file_upload',
        ),
    ]