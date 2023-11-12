"""Zalando sales/return reports processing code lives here.

Reports from Zalando about sales and returns are stored in Dropbox from where
they are grabbed for further processing.

"""
import csv
import os
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from m13.lib.csv_reader import read_csv


EXPECTED_TYPES = [
    "Cancelation",
    "Man. Refund",
    "Return",
    "Sale",
]


class UnexpectedError(Exception):
    """..."""


@dataclass
class SalesReportRow:
    """
    pai = Platform Access & Integration Fee (MKT/PAI)
    """

    payment_service_fee: Decimal
    pai_fee: Decimal
    price: Decimal
    order_number: str
    order_date: str
    shipment_type: str

    @property
    def shipment(self):
        return self.shipment_type == "Sale"

    @property
    def price_as_str(self):
        """Return in the requested format."""
        return str(abs(self.price)).replace(".", ",")

    @property
    def all_fees(self) -> Decimal:
        """Return summed up fees."""
        return self.pai_fee + self.payment_service_fee

    @property
    def all_fees_as_str(self) -> str:
        """Return summed up fees."""
        return str(round(abs(self.all_fees), 2)).replace(".", ",")


def transform_monthly_sales_report(path) -> list:
    """Transform monthly sales reports from Zalando.

    Transform monthly sales reports from Zalando into format which can be
    imported into DATEV.

    Convert all fees back and forth, either it was a sale (shipment) or a
    retoure.

    pp line
    {
        'Currency': 'EUR',
        'Document Date': '03.10.2023',
        'EAN': '781491975427',
        'Fee Category': 'e',
        'Fulfillment Type': 'PARTNER',
        'Gross Partner Revenue': '37.95',
        'MKT/PAI': '-2.11',
        'Merchant UU-ID': 'bc4d3887-12ab-49d3-bf97-c750f7484797',
        'ORDER_DATE': '17.09.2023',
        'Partner': 'MANUFAKTUR DREIZEHN UG (HAFTUNGSBESCHRÄN.KT)',
        'Partner Shipping/Return Date': '03.10.2023',
        'Payment Service Fee': '-0.59',
        'Settled already': 'yes',
        'Subtype': 'Standard',
        'Type': 'Return',
        'Withheld VAT': '0.00',
        'Zalando Order Number': '10101508256167'
    }

    """
    all_rows = []
    for line in read_csv(path, delimiter=","):
        try:
            shipment_type = line["Type"]
            if shipment_type not in EXPECTED_TYPES:
                raise UnexpectedError(f"UNEXPCTED TYPE DIGGI: {shipment_type}")

            comment = f"{line['Type']} : {line['Subtype']}"

            row = SalesReportRow(
                price=Decimal(line["Gross Partner Revenue"]),
                pai_fee=Decimal(line["MKT/PAI"]),
                payment_service_fee=Decimal(line["Payment Service Fee"]),
                order_number=line["Zalando Order Number"],
                order_date=line["ORDER_DATE"],
                shipment_type=line["Type"],
            )
            all_rows.append(row)
        except KeyError as e:
            raise UnexpectedError(f"BOOM - KEYERROR: {str(e)}")

    # Aufwandskonto Gebühren Onlinehandel (mit/ohne USt ?)
    ACCOUNT_ONLINE_FEE = 3101
    # Erlöse 19% Zalando
    NINETEEN_PERCENT_GERMANY_ZALANDO = 8402
    # Verrechnungskonto Zalando
    ZALANDO_OFFSET_ACCOUNT = 12800

    result_rows = []
    for row in all_rows:
        print(row)
        order_event_time = datetime.strptime(row.order_date, "%d.%m.%Y")
        order_date_in_datev_fmt = order_event_time.strftime("%d%m")

        result_rows.append(
            {
                "Umsatz (ohne Soll/Haben-Kz)": row.price_as_str,
                "Soll/Haben-Kennzeichen": ("S" if row.shipment else "H"),
                "WKZ Umsatz": "",
                "Kurs": "",
                "Basis-Umsatz": "",
                "WKZ Basis-Umsatz": "",
                "Konto": ZALANDO_OFFSET_ACCOUNT,
                "Gegenkonto (ohne BU-Schlüssel)": NINETEEN_PERCENT_GERMANY_ZALANDO,
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
                "Konto": ZALANDO_OFFSET_ACCOUNT,
                "Gegenkonto (ohne BU-Schlüssel)": ACCOUNT_ONLINE_FEE,
                "BU-Schlüssel": 9,
                "Belegdatum": order_date_in_datev_fmt,
                "Belegfeld 1": row.order_number,
                "Belegfeld 2": "",
                "Skonto": "",
                "Buchungstext": f"{comment}",
            }
        )

    return result_rows


def dump_result_to_file(result_rows: list, path: str = "result.csv"):
    """Write out list of rows into csv on disk."""
    EXPORT_FIELDS = [
        "Umsatz (ohne Soll/Haben-Kz)",  # Brutto Verkaufspreis
        "Soll/Haben-Kennzeichen",  # S (Verkauf) | H (Retoure)
        "WKZ Umsatz",  # Waehrung
        "Kurs",  # Wechselkurs falls verfugbar
        "Basis-Umsatz",  # Betrag
        "WKZ Basis-Umsatz",  # EUR
        "Konto",  # Verrechnungskonto (ACCOUNTING_MAP)
        "Gegenkonto (ohne BU-Schlüssel)",  # Erloes/Aufwandskonto
        "BU-Schlüssel",  # 9 wenn Verrechnungskonto 3101
        "Belegdatum",  # Verkaufsdatum ohne punkt (wtf) DDMM
        "Belegfeld 1",  # OrderID
        "Belegfeld 2",  #
        "Skonto",  #
        "Buchungstext",  # Beliebiger Text
    ]
    with open(path, "w", encoding="UTF8") as fd:
        csv_writer = csv.DictWriter(
            fd, EXPORT_FIELDS, delimiter=";", escapechar="\\", quoting=csv.QUOTE_ALL
        )
        csv_writer.writeheader()
        csv_writer.writerows(result_rows)
