# Generated by Django 4.0.2 on 2022-06-22 06:30

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0023_rename_zcosts_zcost'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawDailyShipmentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('article_number', models.CharField(max_length=36)),
                ('cancel', models.BooleanField(default=False)),
                ('channel_order_number', models.CharField(max_length=16)),
                ('order_created', models.DateTimeField()),
                ('order_event_time', models.DateTimeField()),
                ('price_in_cent', models.PositiveIntegerField()),
                ('return_reason', models.CharField(max_length=256)),
                ('returned', models.BooleanField(default=False)),
                ('shipment', models.BooleanField(default=False)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='ZCalculator',
        ),
    ]
