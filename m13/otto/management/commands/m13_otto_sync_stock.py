from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from otto.services.stock import sync_stock


class Command(BaseCommand):
    """Management command to sync stock with marketplace OTTO."""

    help = __doc__

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        sync_stock()
