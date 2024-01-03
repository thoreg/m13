"""Transform report files for monthly sales/returns from Z.

For import into DATEV we need a special format. This function transforms Z
format into somthing which can be imported into DATEV.

"""
import logging

from django.core.management.base import BaseCommand

from zalando.services import sales_report


class Command(BaseCommand):
    help = "Import monthly salesreports file."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Path of the file to import",
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

        result_rows = sales_report.importer.transform_monthly_sales_report(
            kwargs["path"]
        )
        sales_report.importer.dump_result_to_file(result_rows, kwargs["output"])
