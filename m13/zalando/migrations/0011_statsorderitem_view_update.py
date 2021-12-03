# Generated by Django 3.2.9 on 2021-12-02 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zalando', '0010_auto_20211202_2144'),
    ]

    operations = [
        migrations.RunSQL("""
            DROP MATERIALIZED VIEW zalando_orderitem_stats
        """),
        migrations.RunSQL("""
            CREATE MATERIALIZED VIEW zalando_orderitem_stats AS
            SELECT
                row_number() OVER (PARTITION BY true) AS id,
                DATE_TRUNC('month', orig_created_timestamp) AS month,
                fulfillment_status AS status,
                COUNT(id) AS count,
                SUM(price_in_cent)::float/100 AS revenue
            FROM
                zalando_orderitem
            GROUP BY
                month,
                fulfillment_status
            ORDER BY
                month
        """),
    ]
