# Generated by Django 3.2.9 on 2021-12-02 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otto', '0003_statsorderitems'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatsOrderItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateTimeField()),
                ('status', models.CharField(max_length=16)),
                ('count', models.IntegerField()),
                ('revenue', models.FloatField()),
            ],
            options={
                'db_table': 'otto_orderitem_stats',
                'managed': False,
            },
        ),
    ]
