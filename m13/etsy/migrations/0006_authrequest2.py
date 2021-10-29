# Generated by Django 3.2.8 on 2021-10-25 04:22

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy', '0005_auto_20211024_1049'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthRequest2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('verifier', models.CharField(max_length=512)),
                ('code_challenge', models.CharField(max_length=256)),
                ('state', models.CharField(max_length=8)),
                ('auth_code', models.CharField(blank=True, max_length=128, null=True)),
                ('auth_token', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]