import pytest

from zalando.models import DailyShipmentReport
from zalando.services.efficiency_check import get_article_stats, import_daily_shipment_report

FILES = [
    'zalando/tests/fixtures/daily_sales_report_0.csv',
    'zalando/tests/fixtures/daily_sales_report_1.csv',
    'zalando/tests/fixtures/daily_sales_report_2.csv'
]


@pytest.mark.django_db
def test_import_daily_shipment_report():
    """Daily Shipment Report items are created properly - no duplicates on multiple runs."""
    import_daily_shipment_report(FILES[0])
    import_daily_shipment_report(FILES[0])
    import_daily_shipment_report(FILES[0])

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


@pytest.mark.django_db
def test_get_article_stats():
    """CSV files get imported properly (1:1 row_csv:row_db)."""
    import_daily_shipment_report(FILES[0])
    import_daily_shipment_report(FILES[1])
    import_daily_shipment_report(FILES[2])

    daily_shipment_reports = DailyShipmentReport.objects.values()
    assert len(daily_shipment_reports) == 12

    article_stats = get_article_stats()

    assert article_stats == [{
        'article_number': 'women-bom-vi-s',
        'canceled': 0,
        'returned': 1,
        'shipped': 2
    }, {
        'article_number': 'women-bom-da-l',
        'canceled': 0,
        'returned': 0,
        'shipped': 3
    }, {
        'article_number': 'pizza_2_w-l',
        'canceled': 0,
        'returned': 0,
        'shipped': 3
    }, {
        'article_number': 'stra_wings_w-l',
        'canceled': 1,
        'returned': 0,
        'shipped': 2
    }]
