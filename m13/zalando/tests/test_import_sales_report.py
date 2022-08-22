from datetime import datetime, timezone
from decimal import Decimal

import pytest
from freezegun import freeze_time

from zalando.models import SalesReport, SalesReportImport
from zalando.services.sales_report.importer import _import_sales_report


@freeze_time('2013-10-13')
@pytest.mark.django_db
def test_import_sales_report():
    """Import of csv file creates report entries and assigns import file."""
    _import_sales_report(
        'zalando/tests/data/PP_E_131000027080_SAL_MAY_2022_(M)Manufaktur1_DE.CSV', '2022/05')

    sales_report_imports = SalesReportImport.objects.all()
    assert len(sales_report_imports) == 1
    sales_report_import = sales_report_imports[0]
    assert sales_report_import.created == datetime(2013, 10, 13, 0, 0, tzinfo=timezone.utc)
    assert sales_report_import.modified == datetime(2013, 10, 13, 0, 0, tzinfo=timezone.utc)
    assert sales_report_import.month == 202205

    assert SalesReport.objects.filter(import_reference=sales_report_import.id).count() == 9

    sri = SalesReport.objects.all()[0]

    assert sri.created_date == datetime(2022, 5, 23, 0, 0, tzinfo=timezone.utc)
    assert sri.currency == 'EUR'
    assert sri.ean == '781491969891'
    assert sri.id == 1
    assert sri.import_reference_id == 1
    assert sri.month == 5
    assert sri.order_date == datetime(2022, 5, 22, 0, 0, tzinfo=timezone.utc)
    assert sri.order_number == '10103408696726'
    assert sri.partner_provision == Decimal('6.49500')
    assert sri.partner_revenue == Decimal('64.95000')
    assert sri.partner_units == 1
    assert sri.shipping_return_date == datetime(2022, 5, 23, 0, 0, tzinfo=timezone.utc)
    assert sri.year == 2022
    assert sri.short_order_date == '2305'
