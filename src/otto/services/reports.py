"""Otto sales/return reports processing code lives here."""

import calendar
from dataclasses import dataclass
from decimal import Decimal

from otto.models import OrderItem

OTTO_PROVISION_IN_PERCENT = Decimal("15")


class UnexpectedError(Exception):
    """..."""


def _r(value):
    """Return rounded value."""
    return round(value, 2)


@dataclass
class SalesReportRow:
    """'Einzeltransaktion's item for OTTO sales."""

    price: Decimal
    order_number: str
    order_date: str
    shipment_type: str

    @property
    def fee(self):
        return _r(self.price * OTTO_PROVISION_IN_PERCENT / 100)

    @property
    def shipment(self):
        return self.shipment_type == "SENT"

    @property
    def price_as_str(self):
        """Return in the requested format."""
        return str(self.price).replace(".", ",")

    @property
    def all_fees(self) -> Decimal:
        """OTTO has only its fixed one fee percent thing."""
        return self.fee

    @property
    def all_fees_as_str(self) -> str:
        """Return summed up fees."""
        return str(round(abs(self.all_fees), 2)).replace(".", ",")


def transform_monthly_sales_report(year: str, month: str) -> list:
    """Transform monthly sales information from Otto into DATEV format.

    The DATEV CSV is based on the orderitems which we have in the db.

    OrderItem looks like:

    {
        '_state': <django.db.models.base.ModelState object at 0x105790c50>,
        'article_number': 'S011P0GIE31P2',
        'cancellation_date': None,
        'carrier': None,
        'carrier_service_code': None,
        'created': datetime.datetime(
            2023, 1, 1, 23, 0, 6, 914000, tzinfo=datetime.timezone.utc),
        'currency': 'EUR',
        'ean': '0781491970002',
        'expected_delivery_date': datetime.datetime(
            2023, 1, 12, 11, 0, tzinfo=datetime.timezone.utc),
        'fulfillment_status': 'RETURNED',
        'id': 5584,
        'modified': datetime.datetime(
            2023, 7, 24, 16, 43, 59, 118000, tzinfo=datetime.timezone.utc),
        'order_id': 4674,
        'position_item_id': 'e00c34f4-5992-4b0d-957c-debc8ad1c993',
        'price_in_cent': 6995,
        'product_title': 'Manufaktur13 Blouson »Women Bomberjacke ...',
        'returned_date': None,
        'sent_date': None,
        'sku': 'women-bom-da-xl',
        'tracking_number': None,
        'vat_rate': 19
    }

    """
    last_day_of_month = calendar.monthrange(int(year), int(month))[1]
    range_from = f"{year}-{month}-01 00:00:00"
    range_to = f"{year}-{month}-{last_day_of_month} 23:59:59"
    all_orderitems = OrderItem.objects.filter(
        created__range=[range_from, range_to],
    )

    # print(f"Here we go ... all items from {range_from} -> {range_to}")
    # for oi in all_orderitems:
    #     print(
    #         oi.created,
    #         oi.modified,
    #         oi.article_number,
    #         oi.price_in_cent,
    #         oi.fulfillment_status,
    #     )
    #     # import ipdb; ipdb.set_trace()

    all_rows = []
    for line in all_orderitems:
        try:
            price = _r(Decimal(line.price_in_cent / 100))
            row = SalesReportRow(
                price=price,
                order_number=line.order.marketplace_order_number,
                order_date=line.order.order_date,
                shipment_type=line.fulfillment_status,
            )
            all_rows.append(row)
        except KeyError as e:
            raise UnexpectedError(f"BOOM - KEYERROR: {str(e)}")

    # Aufwandskonto Gebühren Onlinehandel
    ACCOUNT_ONLINE_FEE = 3101
    # Erlöse 19% OTTO
    NINETEEN_PERCENT_GERMANY_OTTO = 8404
    # Verrechnungskonto OTTO
    OTTO_OFFSET_ACCOUNT = 11500

    result_rows = []
    for row in all_rows:
        order_date_in_datev_fmt = row.order_date.strftime("%d%m")
        result_rows.append(
            {
                "Umsatz (ohne Soll/Haben-Kz)": row.price_as_str,
                "Soll/Haben-Kennzeichen": ("S" if row.shipment else "H"),
                "WKZ Umsatz": "",
                "Kurs": "",
                "Basis-Umsatz": "",
                "WKZ Basis-Umsatz": "",
                "Konto": OTTO_OFFSET_ACCOUNT,
                "Gegenkonto (ohne BU-Schlüssel)": NINETEEN_PERCENT_GERMANY_OTTO,
                "BU-Schlüssel": "",
                "Belegdatum": order_date_in_datev_fmt,
                "Belegfeld 1": row.order_number,
                "Belegfeld 2": "",
                "Skonto": "",
                "Buchungstext": "Verkauf" if row.shipment else "Retoure",
            }
        )
        result_rows.append(
            {
                "Umsatz (ohne Soll/Haben-Kz)": row.all_fees_as_str,
                "Soll/Haben-Kennzeichen": ("H" if row.shipment else "S"),
                "WKZ Umsatz": "",
                "Kurs": "",
                "Basis-Umsatz": "",
                "WKZ Basis-Umsatz": "",
                "Konto": OTTO_OFFSET_ACCOUNT,
                "Gegenkonto (ohne BU-Schlüssel)": ACCOUNT_ONLINE_FEE,
                "BU-Schlüssel": 9,
                "Belegdatum": order_date_in_datev_fmt,
                "Belegfeld 1": row.order_number,
                "Belegfeld 2": "",
                "Skonto": "",
                "Buchungstext": "Gebühr Verkauf" if row.shipment else "Gebühr Retoure",
            }
        )

    return result_rows
