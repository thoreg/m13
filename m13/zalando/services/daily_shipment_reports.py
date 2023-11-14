import logging
from enum import StrEnum

from core.models import MarketplaceConfig, Price
from core.services.article_stats import Marketplace
from m13.lib import log as mlog
from m13.lib.csv_reader import read_csv
from zalando.models import (
    DailyShipmentReport,
    RawDailyShipmentReport,
    TransactionFileUpload,
)

LOG = logging.getLogger(__name__)

LACK_OF_DATA_MSG = "{'lack_of_data': 'No data exists for the selected time range.'}"


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
            if line == LACK_OF_DATA_MSG:
                LOG.info(LACK_OF_DATA_MSG)
                return

            mlog.error(LOG, line)
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

        price, _created = Price.objects.get_or_create(
            sku=line[keys.ARTICLE_NUMBER],
        )

        marketplace_config = MarketplaceConfig.objects.get(
            name=Marketplace.ZALANDO, active=True
        )

        RawDailyShipmentReport.objects.get_or_create(
            price=price,
            article_number=line[keys.ARTICLE_NUMBER],
            cancel=canceled,
            channel_order_number=line[keys.CHANNEL_ORDER_NUMBER],
            order_created=line[keys.ORDER_CREATED],
            order_event_time=line[keys.ORDER_EVENT_TIME],
            price_in_cent=price_in_cent,
            return_reason=line[keys.RETURN_REASON],
            returned=returned,
            shipment=shipped,
            marketplace_config=marketplace_config,
        )

    file.processed = True
    file.save()
