import pytest
from django.test import TestCase

from zalando.models import DailyShipmentReport, TransactionFileUpload, ZProduct
from zalando.services.efficiency_check import get_product_stats, import_daily_shipment_report


class TestWhateverFunctions(TestCase):

    def setUp(self):
        self.file0 = TransactionFileUpload.objects.create(
            file_name='daily_sales_report_0.csv',
            original_csv='zalando/tests/fixtures/daily_sales_report_0.csv',
            processed=False
        )
        self.file1 = TransactionFileUpload.objects.create(
            file_name='daily_sales_report_1.csv',
            original_csv='zalando/tests/fixtures/daily_sales_report_1.csv',
            processed=False
        )
        self.file2 = TransactionFileUpload.objects.create(
            file_name='daily_sales_report_2.csv',
            original_csv='zalando/tests/fixtures/daily_sales_report_2.csv',
            processed=False
        )

    def test_import_daily_shipment_report(self):
        """Daily Shipment Report items are created properly - no duplicates on multiple runs."""
        import_daily_shipment_report(self.file0)
        import_daily_shipment_report(self.file0)
        import_daily_shipment_report(self.file0)

        daily_shipment_reports = DailyShipmentReport.objects.values()
        # Four lines within the input file
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

    def test_get_product_stats(self):
        """CSV files get imported properly (1:1 row_csv:row_db)."""
        import_daily_shipment_report(self.file0)
        import_daily_shipment_report(self.file1)
        import_daily_shipment_report(self.file2)

        daily_shipment_reports = DailyShipmentReport.objects.values()
        assert len(daily_shipment_reports) == 12

        article_stats = get_product_stats()

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

        assert ZProduct.objects.count() == 4
