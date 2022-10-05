# Generated by Django 4.0.2 on 2022-10-04 06:27

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mirapodo', '0004_order_mail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('carrier', models.CharField(max_length=128)),
                ('tracking_info', models.CharField(max_length=256)),
                ('response_status_code', models.PositiveSmallIntegerField()),
                ('response', models.TextField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mirapodo.order')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]