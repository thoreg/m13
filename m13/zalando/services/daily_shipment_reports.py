import logging
from enum import StrEnum

from django.db import connection

from m13.lib.csv_reader import read_csv
from m13.lib.psql import dictfetchall
from zalando.models import (
    DailyShipmentReport,
    RawDailyShipmentReport,
    TransactionFileUpload,
    ZProduct,
)

LOG = logging.getLogger(__name__)


class FieldsV0(StrEnum):
    """Field mapping for the original version."""

    ARTICLE_NAME = "Article Name"
    ARTICLE_NUMBER = "Article Number"
    CANCELLATION = "Cancellation"
    CANCELLATION_REASON = "Cancellation Reason"
    CHANNEL_ARTICLE_NUMBER = "Channel Article Number"
    CHANNEL_ORDER_NUMBER = "Channel Order Number"
    CR_ORDER_NUMBER = "CR Order Number"
    EAN = "EAN"
    FULFILLING_STORE = "Fulfilling Store"
    GENERATING_STORE = "Generating Store"
    INVOICE_NUMBER = "Invoice Number"
    ORDER_CREATED = "Order Created"
    ORDER_EVENT_TIME = "Order Event Time"
    PRICE = "Price"
    RETURN = "Return"
    RETURN_REASON = "Return Reason"
    RETURN_TRACKING_NUMBER = "Return Tracking Number"
    SHIPMENT = "Shipment"
    TRACKING_NUMBER = "Tracking Number"
    ZIP_CODE = "Zip Code"


class FieldsV1(StrEnum):
    """Crazy pot heads changing fields on the fly at zalando."""

    ARTICLE_NAME = "article_name"
    ARTICLE_NUMBER = "article_number"
    CANCELLATION = "cancellation"
    CANCELLATION_REASON = "line_cancellation_reason"
    CHANNEL_ARTICLE_NUMBER = "channel_article_number"
    CHANNEL_ORDER_NUMBER = "channel_order_number"
    CR_ORDER_NUMBER = "cr_order_number"
    EAN = "ean"
    FULFILLING_STORE = "fulfilling_store"
    GENERATING_STORE = "generating_store"
    INVOICE_NUMBER = "invoice_number"
    ORDER_CREATED = "order_created_at"
    ORDER_EVENT_TIME = "order_event_time"
    PRICE = "line_price_amount"
    RETURN = "return"
    RETURN_REASON = "line_return_reason"
    RETURN_TRACKING_NUMBER = "return_tracking_number"
    SHIPMENT = "shipment"
    TRACKING_NUMBER = "delivery_tracking_number"
    ZIP_CODE = "zip_code"


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
        if sorted([k for k in line])[0] == "Article Name":
            keys = FieldsV0
        elif sorted([k for k in line])[0] == "article_name":
            keys = FieldsV1
        else:
            LOG.error(line)
            LOG.exception("unknown line format in daily shipment report")
            return

        canceled = line[keys.CANCELLATION] == "x"
        returned = line[keys.RETURN] == "x"
        shipped = line[keys.SHIPMENT] == "x"

        price_in_cent = float(line[keys.PRICE]) * 100

        DailyShipmentReport.objects.get_or_create(
            article_number=line[keys.ARTICLE_NUMBER],
            cancel=canceled,
            channel_order_number=line[keys.CHANNEL_ORDER_NUMBER],
            order_created=line[keys.ORDER_CREATED],
            price_in_cent=price_in_cent,
            return_reason=line[keys.RETURN_REASON],
            returned=returned,
            shipment=shipped,
        )

        product, _created = ZProduct.objects.get_or_create(
            article=line[keys.ARTICLE_NUMBER],
        )

        RawDailyShipmentReport.objects.get_or_create(
            zproduct=product,
            article_number=line[keys.ARTICLE_NUMBER],
            cancel=canceled,
            channel_order_number=line[keys.CHANNEL_ORDER_NUMBER],
            order_created=line[keys.ORDER_CREATED],
            order_event_time=line[keys.ORDER_EVENT_TIME],
            price_in_cent=price_in_cent,
            return_reason=line[keys.RETURN_REASON],
            returned=returned,
            shipment=shipped,
        )

    file.processed = True
    file.save()

    # Update the product stats after each import
    get_product_stats()


def get_product_stats():
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    article_stats = {}
    with connection.cursor() as cursor:
        cursor.execute(
            """
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
        """
        )
        article_stats = dictfetchall(cursor)

    for stats in article_stats:
        zp, created = ZProduct.objects.get_or_create(
            article=stats["article_number"],
            defaults=dict(
                shipped=stats["shipped"],
                returned=stats["returned"],
                canceled=stats["canceled"],
            ),
        )
        if created:
            LOG.info(f"ZProduct created : {stats}")
        else:
            zp.shipped = stats["shipped"]
            zp.returned = stats["returned"]
            zp.canceled = stats["canceled"]
            zp.save()

    return article_stats


def get_product_stats_v1(start_date):
    """Return dictionary with aggregated values for number of shipped, returned and canceled."""
    params = {"start_date": start_date}
    with connection.cursor() as cursor:
        query = """
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
        """
        # pprint(cursor.mogrify(query, params).decode('utf8'))
        cursor.execute(query, params)
        result = dictfetchall(cursor)

    return result
