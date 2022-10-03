import logging

from django.db import connection

from m13.lib.csv_reader import read_csv
from m13.lib.psql import dictfetchall
from zalando.models import (DailyShipmentReport, RawDailyShipmentReport, TransactionFileUpload,
                            ZProduct)

LOG = logging.getLogger(__name__)


def import_all_unprocessed_daily_shipment_reports():
    """..."""
    files = TransactionFileUpload.objects.filter(processed=False)
    for file in files:
        import_daily_shipment_report(file)


def import_daily_shipment_report(file: TransactionFileUpload) -> None:
    """Import daily shipment report data for further analytics and reports.

    One row in the database per row from the original CSV.
    """
    for line in read_csv(file.original_csv.name, delimiter=","):

        canceled = line['Cancellation'] == 'x'
        returned = line['Return'] == 'x'
        shipped = line['Shipment'] == 'x'

        price_in_cent = float(line['Price']) * 100

        DailyShipmentReport.objects.get_or_create(
            article_number=line['Article Number'],
            cancel=canceled,
            channel_order_number=line['Channel Order Number'],
            order_created=line['Order Created'],
            price_in_cent=price_in_cent,
            return_reason=line['Return Reason'],
            returned=returned,
            shipment=shipped)

        product, _created = ZProduct.objects.get_or_create(
            article=line['Article Number'],
        )

        RawDailyShipmentReport.objects.get_or_create(
            zproduct=product,
            article_number=line['Article Number'],
            cancel=canceled,
            channel_order_number=line['Channel Order Number'],
            order_created=line['Order Created'],
            order_event_time=line['Order Event Time'],
            price_in_cent=price_in_cent,
            return_reason=line['Return Reason'],
            returned=returned,
            shipment=shipped)

    file.processed = True
    file.save()

    # Update the product stats after each import
    get_product_stats()


def get_product_stats():
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    article_stats = {}
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                article_number,
                COUNT(shipment) FILTER (WHERE shipment) AS shipped,
                COUNT(returned) FILTER (WHERE returned) AS returned,
                COUNT(cancel) FILTER (WHERE cancel) AS canceled
            FROM
                zalando_dailyshipmentreport
            GROUP BY
                article_number
            ORDER BY
                returned DESC
        ''')
        article_stats = dictfetchall(cursor)

    for stats in article_stats:
        zp, created = ZProduct.objects.get_or_create(
            article=stats['article_number'],
            defaults=dict(
                shipped=stats['shipped'],
                returned=stats['returned'],
                canceled=stats['canceled']
            )
        )
        if created:
            LOG.info(f'ZProduct created : {stats}')
        else:
            zp.shipped = stats['shipped']
            zp.returned = stats['returned']
            zp.canceled = stats['canceled']
            zp.save()

    return article_stats


def get_product_stats_v1(start_date):
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    params = {
        'start_date': start_date
    }
    with connection.cursor() as cursor:
        query = '''
            SELECT
                article_number,
                COUNT(shipment) FILTER (WHERE shipment) AS shipped,
                COUNT(returned) FILTER (WHERE returned) AS returned,
                COUNT(cancel) FILTER (WHERE cancel) AS canceled
            FROM
                zalando_dailyshipmentreport_raw
            WHERE
                order_event_time > %(start_date)s
            GROUP BY
                article_number
            ORDER BY
                returned DESC
        '''
        # pprint(cursor.mogrify(query, params).decode('utf8'))
        cursor.execute(query, params)
        result = dictfetchall(cursor)

    return result
