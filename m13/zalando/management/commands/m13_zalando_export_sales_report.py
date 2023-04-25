"""Export sales report for zalando."""
from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from zalando.services import sales_report


class Command(BaseCommand):
    help = "Export sales report for the requested month."

    def add_arguments(self, parser):
        parser.add_argument(
            "from",
            type=str,
            help="e.g. '2022-05-01 00:00:00'",
        )
        parser.add_argument(
            "to",
            type=str,
            help="e.g. '2022-05-31 23:59:59'",
        )

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        sales_report.exporter.export_sales_report(kwargs["from"], kwargs["to"])
