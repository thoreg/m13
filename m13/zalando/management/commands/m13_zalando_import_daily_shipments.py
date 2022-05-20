import logging
from functools import reduce

from django.conf import settings
from django.core.management.base import BaseCommand

from zalando.services.shipments import import_all_unprocessed_daily_shipment_reports

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import daily shipment reports."

    def handle(self, *args, **kwargs):
        """..."""
        import_all_unprocessed_daily_shipment_reports()
