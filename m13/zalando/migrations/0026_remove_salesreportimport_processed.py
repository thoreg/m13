# Generated by Django 4.0.2 on 2022-07-13 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0025_salesreport_import_reference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salesreportimport',
            name='processed',
        ),
    ]