"""Export sales report for zalando in DATEV compatible format.

python manage.py m13_zalando_export_sales_report 2024 12 2024-12-zalando-single-transactions.csv

"""
import calendar

from django.core.management.base import BaseCommand

from m13.lib import finance_reports
from zalando.models import SalesReport
from zalando.services import reports


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "year",
            type=str,
            help="e.g. '2024'",
        )
        parser.add_argument(
            "month",
            type=str,
            help="e.g. '01'",
        )
        parser.add_argument(
            "output",
            type=str,
            help="e.g. '2024-01-zalando-single-transactions.csv'",
        )

    def handle(self, *args, **kwargs):
        """..."""
        year = kwargs["year"]
        month = kwargs["month"]
        last_day_of_month = calendar.monthrange(int(year), int(month))[1]
        range_from = f"{year}-{month}-01 00:00:00"
        range_to = f"{year}-{month}-{last_day_of_month} 23:59:59"

        result_rows = reports.export(range_from, range_to)
        finance_reports.dump_result_to_file(result_rows, kwargs["output"])
