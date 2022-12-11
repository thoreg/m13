
from django.contrib.auth.models import User
from freezegun import freeze_time
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient, APITestCase

from core.models import Category
from zalando.models import (DailyShipmentReport, RawDailyShipmentReport, TransactionFileUpload,
                            ZProduct)
from zalando.services.daily_shipment_reports import (get_product_stats, get_product_stats_v1,
                                                     import_daily_shipment_report)


class TestWhateverFunctions(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='jon',
            email='user@foo.com',
            password='12345')

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
        raw_daily_shipment_reports = RawDailyShipmentReport.objects.values()
        # Four lines within the input file
        assert len(daily_shipment_reports) == 4
        assert len(raw_daily_shipment_reports) == 4

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
        raw_daily_shipment_reports = RawDailyShipmentReport.objects.values()
        assert len(raw_daily_shipment_reports) == 12

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

    @freeze_time('2022-04-01')
    def test_get_product_stats_v2(self):
        import_daily_shipment_report(self.file0)
        import_daily_shipment_report(self.file1)
        import_daily_shipment_report(self.file2)

        daily_shipment_reports = DailyShipmentReport.objects.values()
        raw_daily_shipment_reports = RawDailyShipmentReport.objects.values()

        # Four lines within the input file
        assert len(daily_shipment_reports) == 12
        assert len(raw_daily_shipment_reports) == 12

        # Service is available and does some filtering for date range
        assert get_product_stats_v1('2022-04-01') == [
            {'article_number': 'women-bom-vi-s', 'canceled': 0, 'returned': 1, 'shipped': 2},
            {'article_number': 'women-bom-da-l', 'canceled': 0, 'returned': 0, 'shipped': 3},
            {'article_number': 'pizza_2_w-l', 'canceled': 0, 'returned': 0, 'shipped': 3},
            {'article_number': 'stra_wings_w-l', 'canceled': 1, 'returned': 0, 'shipped': 2},
        ]

        assert get_product_stats_v1('2022-05-01') == [
            {'article_number': 'women-bom-vi-s', 'canceled': 0, 'returned': 0, 'shipped': 2},
            {'article_number': 'women-bom-da-l', 'canceled': 0, 'returned': 0, 'shipped': 2},
            {'article_number': 'pizza_2_w-l', 'canceled': 0, 'returned': 0, 'shipped': 2},
            {'article_number': 'stra_wings_w-l', 'canceled': 0, 'returned': 0, 'shipped': 2},
        ]

        assert get_product_stats_v1('2022-06-01') == [
            {'article_number': 'women-bom-vi-s', 'canceled': 0, 'returned': 0, 'shipped': 1},
            {'article_number': 'women-bom-da-l', 'canceled': 0, 'returned': 0, 'shipped': 1},
            {'article_number': 'pizza_2_w-l', 'canceled': 0, 'returned': 0, 'shipped': 1},
            {'article_number': 'stra_wings_w-l', 'canceled': 0, 'returned': 0, 'shipped': 1},
        ]

        self.client.login(username='jon', password='12345')

        #
        # No category - No filter
        #
        response = self.client.get('/api/v1/zalando/finance/products/')
        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            'N/A': {
                'content': [
                    {'article_number': 'women-bom-vi-s',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 1,
                     'shipped': 2,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'women-bom-da-l',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 3,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'pizza_2_w-l',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 3,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'stra_wings_w-l',
                     'canceled': 1,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 2,
                     'shipping_costs': '3.55',
                     'vk_zalando': None}],
                'name': 'N/A',
                'stats': {
                    'canceled': 1,
                    'returned': 1,
                    'shipped': 10,
                    'total_diff': 0,
                    'total_return_costs': 0,
                    'total_revenue': 0}}}

        #
        # No category - Filter by DateRange
        #
        response = self.client.get('/api/v1/zalando/finance/products/?start=2022-06-01')
        assert response.status_code == HTTP_200_OK

        assert response.json() == {
            'N/A': {
                'content': [
                    {'article_number': 'women-bom-vi-s',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 1,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'women-bom-da-l',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 1,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'pizza_2_w-l',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 1,
                     'shipping_costs': '3.55',
                     'vk_zalando': None},
                    {'article_number': 'stra_wings_w-l',
                     'canceled': 0,
                     'category': 'N/A',
                     'costs_production': None,
                     'eight_percent_provision': None,
                     'generic_costs': None,
                     'nineteen_percent_vat': None,
                     'profit_after_taxes': None,
                     'return_costs': '3.55',
                     'returned': 0,
                     'shipped': 1,
                     'shipping_costs': '3.55',
                     'vk_zalando': None}],
                'name': 'N/A',
                'stats': {
                    'canceled': 0,
                    'returned': 0,
                    'shipped': 4,
                    'total_diff': 0,
                    'total_return_costs': 0,
                    'total_revenue': 0}}}

        # Same shit but different - category defined for two of the products
        category = Category.objects.create(name='THIS_IS_A_VERY_VERY_LONG_CATEGORY_NAME')
        for sku in ['women-bom-vi-s', 'women-bom-da-l']:
            zproduct = ZProduct.objects.get(article=sku)
            zproduct.category = category
            zproduct.costs_production = 49.50
            zproduct.vk_zalando = 69.99
            zproduct.save()

        #
        # One categroy for two products - Filter by DateRange
        #
        response = self.client.get('/api/v1/zalando/finance/products/?start=2022-06-01')
        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            'N/A': {
                'content': [{
                    'article_number': 'pizza_2_w-l',
                    'canceled': 0,
                    'category': 'N/A',
                    'costs_production': None,
                    'eight_percent_provision': None,
                    'generic_costs': None,
                    'nineteen_percent_vat': None,
                    'profit_after_taxes': None,
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 1,
                    'shipping_costs': '3.55',
                    'vk_zalando': None},
                   {'article_number': 'stra_wings_w-l',
                    'canceled': 0,
                    'category': 'N/A',
                    'costs_production': None,
                    'eight_percent_provision': None,
                    'generic_costs': None,
                    'nineteen_percent_vat': None,
                    'profit_after_taxes': None,
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 1,
                    'shipping_costs': '3.55',
                    'vk_zalando': None}],
                'name': 'N/A',
                'stats': {
                    'canceled': 0,
                    'returned': 0,
                    'shipped': 2,
                    'total_diff': 0,
                    'total_return_costs': 0,
                    'total_revenue': 0
                }
            },
            'THIS_IS_A_VERY_VER': {
                'content': [{
                    'article_number': 'women-bom-vi-s',
                    'canceled': 0,
                    'category': 'THIS_IS_A_VERY_VERY_LONG_CATEGORY_NAME',
                    'costs_production': '49.50',
                    'eight_percent_provision': '-5.18',
                    'generic_costs': '2.10',
                    'nineteen_percent_vat': '-11.17',
                    'profit_after_taxes': '2.69',
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 1,
                    'shipping_costs': '3.55',
                    'total_diff': '2.69',
                    'total_return_costs': '0.00',
                    'total_revenue': '2.69',
                    'vk_zalando': '69.99'
                }, {
                    'article_number': 'women-bom-da-l',
                    'canceled': 0,
                    'category': 'THIS_IS_A_VERY_VERY_LONG_CATEGORY_NAME',
                    'costs_production': '49.50',
                    'eight_percent_provision': '-5.18',
                    'generic_costs': '2.10',
                    'nineteen_percent_vat': '-11.17',
                    'profit_after_taxes': '2.69',
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 1,
                    'shipping_costs': '3.55',
                    'total_diff': '2.69',
                    'total_return_costs': '0.00',
                    'total_revenue': '2.69',
                    'vk_zalando': '69.99'}],
                'name': 'THIS_IS_A_VERY_VER',
                'stats': {
                    'canceled': 0,
                    'returned': 0,
                    'shipped': 2,
                    'total_diff': '5.38',
                    'total_return_costs': '0.00',
                    'total_revenue': '5.38'}
            }
        }
        #
        # One category for two products - No filter
        #
        response = self.client.get('/api/v1/zalando/finance/products/')
        assert response.status_code == HTTP_200_OK
        assert response.json() == {
            'N/A': {
                'content': [{
                    'article_number': 'pizza_2_w-l',
                    'canceled': 0,
                    'category': 'N/A',
                    'costs_production': None,
                    'eight_percent_provision': None,
                    'generic_costs': None,
                    'nineteen_percent_vat': None,
                    'profit_after_taxes': None,
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 3,
                    'shipping_costs': '3.55',
                    'vk_zalando': None},
                   {'article_number': 'stra_wings_w-l',
                    'canceled': 1,
                    'category': 'N/A',
                    'costs_production': None,
                    'eight_percent_provision': None,
                    'generic_costs': None,
                    'nineteen_percent_vat': None,
                    'profit_after_taxes': None,
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 2,
                    'shipping_costs': '3.55',
                    'vk_zalando': None}],
                'name': 'N/A',
                'stats': {
                    'canceled': 1,
                    'returned': 0,
                    'shipped': 5,
                    'total_diff': 0,
                    'total_return_costs': 0,
                    'total_revenue': 0
                }
            },
            'THIS_IS_A_VERY_VER': {
                'content': [{
                    'article_number': 'women-bom-vi-s',
                    'canceled': 0,
                    'category': 'THIS_IS_A_VERY_VERY_LONG_CATEGORY_NAME',
                    'costs_production': '49.50',
                    'eight_percent_provision': '-5.18',
                    'generic_costs': '2.10',
                    'nineteen_percent_vat': '-11.17',
                    'profit_after_taxes': '2.69',
                    'return_costs': '3.55',
                    'returned': 1,
                    'shipped': 2,
                    'shipping_costs': '3.55',
                    'total_diff': '-6.51',
                    'total_return_costs': '9.20',
                    'total_revenue': '2.69',
                    'vk_zalando': '69.99'
                }, {
                    'article_number': 'women-bom-da-l',
                    'canceled': 0,
                    'category': 'THIS_IS_A_VERY_VERY_LONG_CATEGORY_NAME',
                    'costs_production': '49.50',
                    'eight_percent_provision': '-5.18',
                    'generic_costs': '2.10',
                    'nineteen_percent_vat': '-11.17',
                    'profit_after_taxes': '2.69',
                    'return_costs': '3.55',
                    'returned': 0,
                    'shipped': 3,
                    'shipping_costs': '3.55',
                    'total_diff': '8.07',
                    'total_return_costs': '0.00',
                    'total_revenue': '8.07',
                    'vk_zalando': '69.99'}],
                'name': 'THIS_IS_A_VERY_VER',
                'stats': {
                    'canceled': 0,
                    'returned': 1,
                    'shipped': 5,
                    'total_diff': '1.56',
                    'total_return_costs': '9.20',
                    'total_revenue': '10.76'}
            }
        }
