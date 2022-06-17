import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from zalando.services.orders import process_new_oea_records

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import orders out from stored order event api msgs."

    def handle(self, *args, **kwargs):
        """..."""
        try:
            process_new_oea_records()
        except Exception as exc:
            send_mail(
                'M13BM - Import of Zalando Orders failed',
                f'{str(exc)}',
                settings.FROM_EMAIL_ADDRESS,
                settings.ADMINS,
                fail_silently=False)
