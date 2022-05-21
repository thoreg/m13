import pytest

from zalando.models import DailyShipmentReport
from zalando.services.efficiency_check import import_daily_shipment_report

FILE_NAME = 'zalando/tests/fixtures/daily_sales_report_0.csv'


@pytest.mark.django_db
def test_import_daily_shipment_report():
    """Daily Shipment Report items are created properly - no duplicates on multiple runs."""
    import_daily_shipment_report(FILE_NAME)
    import_daily_shipment_report(FILE_NAME)
    import_daily_shipment_report(FILE_NAME)

    daily_shipment_reports = DailyShipmentReport.objects.values()
    assert len(daily_shipment_reports) == 4

    assert daily_shipment_reports[0]['shipment'] is True
    assert daily_shipment_reports[0]['returned'] is False
    assert daily_shipment_reports[0]['cancel'] is False

    assert daily_shipment_reports[1]['shipment'] is False
    assert daily_shipment_reports[1]['returned'] is False
    assert daily_shipment_reports[1]['cancel'] is True

    assert daily_shipment_reports[2]['shipment'] is True
    assert daily_shipment_reports[2]['returned'] is False
    assert daily_shipment_reports[2]['cancel'] is False

    assert daily_shipment_reports[3]['shipment'] is False
    assert daily_shipment_reports[3]['returned'] is True
    assert daily_shipment_reports[3]['cancel'] is False
