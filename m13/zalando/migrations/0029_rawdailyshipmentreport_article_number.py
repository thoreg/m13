# Generated by Django 4.0.2 on 2022-07-15 11:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zalando", "0028_alter_rawdailyshipmentreport_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawdailyshipmentreport",
            name="article_number",
            field=models.CharField(default="", max_length=32),
            preserve_default=False,
        ),
    ]
