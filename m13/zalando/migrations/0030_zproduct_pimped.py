# Generated by Django 4.0.2 on 2022-10-26 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0029_rawdailyshipmentreport_article_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='zproduct',
            name='pimped',
            field=models.BooleanField(default=False),
        ),
    ]
