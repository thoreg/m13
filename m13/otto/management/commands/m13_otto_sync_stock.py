from django.core.management.base import BaseCommand

from otto.services.stock import sync_stock


class Command(BaseCommand):
    """Management command to sync stock with marketplace OTTO."""

    help = __doc__

    def handle(self, *args, **kwargs):
        """..."""
        sync_stock()
