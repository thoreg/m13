"""Import orders from marketplace mirapodo."""
from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from mirapodo.services import orders


class Command(BaseCommand):
    help = "Import orders from marketplace mirapodo."

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        orders.fetch_orders()
