"""Create report about single transactions for OTTO orders.

The report needs to be in a format which can be importet to DATEV.

"""
import logging

from django.core.management.base import BaseCommand

from otto.services import reports as otto_reports


class Command(BaseCommand):
    help = "Import monthly salesreports file."

    def add_arguments(self, parser):
        parser.add_argument(
            "year",
            type=str,
            help="Year of the daterange",
        )
        parser.add_argument(
            "month",
            type=str,
            help="Month of the daterange",
        )
        parser.add_argument(
            "output",
            type=str,
            help="Path to the result ",
        )

    def handle(self, *args, **kwargs):
        """..."""
        verbosity = int(kwargs["verbosity"])
        root_logger = logging.getLogger("")
        if verbosity > 1:
            root_logger.setLevel(logging.DEBUG)

        result_rows = otto_reports.transform_monthly_sales_report(
            kwargs["year"], kwargs["month"]
        )
        otto_reports.dump_result_to_file(result_rows, kwargs["output"])
