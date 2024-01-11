import pytest

from zalando.services.sales_report.importer import transform_monthly_sales_report


@pytest.mark.django_db
def test_transform_monthly_sales_report():
    """Import of csv file creates report entries and assigns import file."""
    result_rows = transform_monthly_sales_report(
        "zalando/tests/data/Sales_Report_JAN_2023.csv"
    )
    assert result_rows == [
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "49,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Sale : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "2,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "49,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Sale : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "2,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "49,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1701",
            "Belegfeld 1": "10104461645953",
            "Belegfeld 2": "",
            "Buchungstext": "Sale : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "2,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1301",
            "Belegfeld 1": "10103460824904",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "49,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1301",
            "Belegfeld 1": "10103460824904",
            "Belegfeld 2": "",
            "Buchungstext": "Sale : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "2,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1501",
            "Belegfeld 1": "10103461095076",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "49,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1501",
            "Belegfeld 1": "10103461095076",
            "Belegfeld 2": "",
            "Buchungstext": "Sale : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "2,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
    ]

    result_rows = transform_monthly_sales_report(
        "zalando/tests/data/Sales_Report_OCT_2023.csv"
    )

    assert result_rows == [
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1109",
            "Belegfeld 1": "10101507189015",
            "Belegfeld 2": "",
            "Buchungstext": "Retoure",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "69,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1109",
            "Belegfeld 1": "10101507189015",
            "Belegfeld 2": "",
            "Buchungstext": "Return : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "10,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "1709",
            "Belegfeld 1": "10101508256167",
            "Belegfeld 2": "",
            "Buchungstext": "Retoure",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "37,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "1709",
            "Belegfeld 1": "10101508256167",
            "Belegfeld 2": "",
            "Buchungstext": "Return : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "2,70",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "3009",
            "Belegfeld 1": "10101510632689",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "69,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "3009",
            "Belegfeld 1": "10101510632689",
            "Belegfeld 2": "",
            "Buchungstext": "Return : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "10,56",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "0210",
            "Belegfeld 1": "10101510989314",
            "Belegfeld 2": "",
            "Buchungstext": "Verkauf",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "59,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "0210",
            "Belegfeld 1": "10101510989314",
            "Belegfeld 2": "",
            "Buchungstext": "Return : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "13,25",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": "",
            "Basis-Umsatz": "",
            "Belegdatum": "0210",
            "Belegfeld 1": "10101510989314",
            "Belegfeld 2": "",
            "Buchungstext": "Retoure",
            "Gegenkonto (ohne BU-Schlüssel)": 8402,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "H",
            "Umsatz (ohne Soll/Haben-Kz)": "59,95",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
        {
            "BU-Schlüssel": 9,
            "Basis-Umsatz": "",
            "Belegdatum": "0210",
            "Belegfeld 1": "10101510989314",
            "Belegfeld 2": "",
            "Buchungstext": "Return : Standard",
            "Gegenkonto (ohne BU-Schlüssel)": 3101,
            "Konto": 12800,
            "Kurs": "",
            "Skonto": "",
            "Soll/Haben-Kennzeichen": "S",
            "Umsatz (ohne Soll/Haben-Kz)": "13,25",
            "WKZ Basis-Umsatz": "",
            "WKZ Umsatz": "",
        },
    ]