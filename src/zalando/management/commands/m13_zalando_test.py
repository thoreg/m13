"""Stub for development."""

import logging

from django.core.management.base import BaseCommand

from zalando.models import SalesReportFileUpload
from zalando.services.reports import import_monthly_sales_report


class Command(BaseCommand):
    help = "Import monthly salesreports file."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Path of the file to import",
        )

    def handle(self, *args, **kwargs):
        """..."""
        verbosity = int(kwargs["verbosity"])
        root_logger = logging.getLogger("")
        if verbosity > 1:
            root_logger.setLevel(logging.DEBUG)

        try:
            srfu = SalesReportFileUpload.objects.get(
                file_name=kwargs["path"],
            )
            import_monthly_sales_report(srfu)
        except SalesReportFileUpload.DoesNotExist:
            print("File not found")
