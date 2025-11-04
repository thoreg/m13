from django.core.management.base import BaseCommand

from aboutyou.services import shipments


class Command(BaseCommand):
    help = "Sync status of batch requests for shipments."

    def handle(self, *args, **kwargs):
        """...."""
        shipments.check_batch_requests()
