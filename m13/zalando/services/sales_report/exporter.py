"""Export Sales Report (for zalando)."""
import csv

from zalando.constants import ZALANDO_OFFSET_ACCOUNT
from zalando.models import SalesReport

EXPORT_FIELDS = [
    'Umsatz (ohne Soll/Haben-Kz)',     # Brutto Verkaufspreis
    'Soll/Haben-Kennzeichen',          # S | H
    'WKZ Umsatz',                      # Waehrung
    'Kurs',                            # Wechselkurs falls verfugbar
    'Basis-Umsatz',                    # Betrag
    'WKZ Basis-Umsatz',                # EUR
    'Konto',                           # Verrechnungskonto (ACCOUNTING_MAP)
    'Gegenkonto (ohne BU-Schlüssel)',  # Erloes/Aufwandskonto
    'BU-Schlüssel',                    # 9 wenn Verrechnungskonto 3101
    'Belegdatum',                      # Verkaufsdatum ohne punkt (wtf) DDMM
    'Belegfeld 1',                     # OrderID
    'Belegfeld 2',                     #
    'Skonto',                          #
    'Buchungstext',                    # Beliebiger Text
]


def export_sales_report(from_order_date, to_order_date):
    """Write result CSV in the requested format.

    Each row has revenue and provision information - the result file has two
    lines (one for revenue one for provision) which go into different target
    account numbers.
    """
    result_list = []
    print(f'Start to export from {from_order_date} to {to_order_date}')
    data = (
        SalesReport
        .objects
        .filter(shipping_return_date__range=(from_order_date, to_order_date))
        .order_by('order_date')
    )

    for row in data:
        for revenue in [True, False]:
            result_list.append({
                'Umsatz (ohne Soll/Haben-Kz)': row.get_abs_value(revenue),
                'Soll/Haben-Kennzeichen': (
                    row.debit_or_credit_indicator_income
                    if revenue else row.debit_or_credit_indicator_fees
                ),
                'WKZ Umsatz': '',
                'Kurs': '',
                'Basis-Umsatz': '',
                'WKZ Basis-Umsatz': '',
                'Konto': ZALANDO_OFFSET_ACCOUNT,
                'Gegenkonto (ohne BU-Schlüssel)': row.get_target(revenue),
                'BU-Schlüssel': row.get_bu_key(revenue),
                'Belegdatum': row.short_order_date,
                'Belegfeld 1': row.order_number,
                'Belegfeld 2': '',
                'Skonto': '',
                'Buchungstext': row.get_description(revenue),
            })

    from_date = from_order_date.split()[0]
    to_date = to_order_date.split()[0]
    path = f'{from_date}_{to_date}_export_zalando_sales_report.csv'
    with open(path, 'w', encoding='UTF8') as fd:
        csv_writer = csv.DictWriter(
            fd, EXPORT_FIELDS,
            delimiter=';',
            escapechar='',
            quoting=csv.QUOTE_ALL)
        csv_writer.writeheader()
        csv_writer.writerows(result_list)
