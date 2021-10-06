# Generated by Django 3.2.6 on 2021-10-06 03:58

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0008_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('store', models.CharField(max_length=8)),
                ('ean', models.CharField(max_length=16, unique=True)),
                ('title', models.CharField(max_length=256)),
                ('price', models.CharField(max_length=8)),
                ('quantity', models.SmallIntegerField()),
                ('article_number', models.CharField(max_length=32)),
                ('color', models.CharField(max_length=32)),
                ('price_overwrite', models.CharField(blank=True, max_length=8, null=True)),
                ('use_row', models.BooleanField(default=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
