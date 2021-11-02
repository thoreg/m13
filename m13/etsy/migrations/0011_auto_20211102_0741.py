# Generated by Django 3.2.8 on 2021-11-02 06:41

import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etsy', '0010_remove_orderitem_article_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGrant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('verifier', models.CharField(max_length=512)),
                ('code_challenge', models.CharField(max_length=256)),
                ('state', models.CharField(max_length=8)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('auth_token', models.CharField(max_length=128)),
                ('refresh_token', models.CharField(max_length=128)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='AuthRequest2',
        ),
    ]