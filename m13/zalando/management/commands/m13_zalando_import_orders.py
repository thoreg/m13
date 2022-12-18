import logging

from django.core.management.base import BaseCommand

from m13.lib.email import send_traceback_as_email
from zalando.services.orders import process_new_oea_records

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import orders out from stored order event api msgs."

    def handle(self, *args, **kwargs):
        """..."""
        try:
            process_new_oea_records()
        except Exception as exc:
            LOG.exception(exc)
            send_traceback_as_email("M13BM - Import of Zalando Orders failed")
