"""Export sales report for zalando."""
from django.core.management.base import BaseCommand

from zalando.services import sales_report


class Command(BaseCommand):
    help = "Export sales report for the requested month."

    def add_arguments(self, parser):
        parser.add_argument(
            'month',
            type=str,
            help="Month of interest, e.g. 2022/01",
        )

    def handle(self, *args, **kwargs):
        """..."""
        sales_report.exporter.export_sales_report(kwargs['month'])
