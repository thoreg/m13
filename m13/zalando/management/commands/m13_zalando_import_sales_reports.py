"""Download report files from Dropbox and import the data."""
from django.core.management.base import BaseCommand

from zalando.services import sales_report


class Command(BaseCommand):
    help = "Import ZIP files with sales reports from Dropbox."

    def add_arguments(self, parser):
        parser.add_argument(
            "month",
            type=str,
            help="Month of interest, e.g. 2022/01",
        )

    def handle(self, *args, **kwargs):
        """..."""
        sales_report.importer.import_sales_reports(kwargs["month"])
