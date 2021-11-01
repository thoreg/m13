# Generated by Django 3.2.8 on 2021-10-31 12:14

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy', '0007_rename_auth_code_authrequest2_refresh_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('buyer_email', models.EmailField(max_length=254)),
                ('buyer_user_id', models.IntegerField()),
                ('city', models.CharField(max_length=128)),
                ('country_code', models.CharField(max_length=32)),
                ('formatted_address', models.CharField(max_length=256)),
                ('zip_code', models.CharField(max_length=32)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('marketplace_order_id', models.CharField(max_length=64)),
                ('marketplace_order_number', models.CharField(max_length=32)),
                ('order_date', models.DateTimeField()),
                ('last_modified_date', models.DateTimeField()),
                ('internal_status', models.CharField(choices=[('IMPORTED', 'Imported'), ('IN_PROGRESS', 'In Progress'), ('SHIPPED', 'Shipped'), ('FINISHED', 'Finished'), ('CANCELED', 'Canceled')], default='IMPORTED', max_length=11)),
                ('delivery_fee', models.JSONField()),
                ('delivery_address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='delivery_address_set', to='etsy.address')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('cancellation_date', models.DateTimeField(blank=True, null=True)),
                ('expected_delivery_date', models.DateTimeField()),
                ('fulfillment_status', models.CharField(max_length=32)),
                ('price_in_cent', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=8)),
                ('position_item_id', models.CharField(max_length=36)),
                ('article_number', models.CharField(max_length=36)),
                ('ean', models.CharField(max_length=16)),
                ('product_title', models.CharField(max_length=256)),
                ('sku', models.CharField(max_length=36)),
                ('vat_rate', models.PositiveSmallIntegerField()),
                ('returned_date', models.DateTimeField(blank=True, null=True)),
                ('sent_date', models.DateTimeField(blank=True, null=True)),
                ('carrier', models.CharField(blank=True, max_length=32, null=True)),
                ('carrier_service_code', models.CharField(blank=True, max_length=128, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=128, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='etsy.order')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        )
    ]
