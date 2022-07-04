
from datetime import datetime, timezone

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
