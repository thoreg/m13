# Generated by Django 4.0.2 on 2022-06-13 04:11

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_category_product_category'),
        ('zalando', '0017_salesreport_salesreportimport_salesreportexport'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZProduct',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='core.article')),
                ('costs_production', models.DecimalField(decimal_places=2, max_digits=6)),
                ('vk_zalando', models.DecimalField(decimal_places=2, max_digits=6)),
                ('shipping_costs', models.DecimalField(decimal_places=2, default=3.55, max_digits=5)),
                ('return_costs', models.DecimalField(decimal_places=2, default=3.55, max_digits=5)),
                ('shipped', models.PositiveIntegerField(blank=True, null=True)),
                ('returned', models.PositiveIntegerField(blank=True, null=True)),
                ('canceled', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
