import logging
from functools import reduce

from django.conf import settings
from django.core.management.base import BaseCommand

from zalando.services.orders import process_new_oea_records

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import orders out from stored order event api msgs."

    def handle(self, *args, **kwargs):
        """..."""
        process_new_oea_records()
