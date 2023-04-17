"""Import orders from marketplace mirapodo."""
from django.core.management.base import BaseCommand

from mirapodo.services import orders


class Command(BaseCommand):
    help = "Import orders from marketplace mirapodo."

    def handle(self, *args, **kwargs):
        """..."""
        orders.fetch_orders()
        return 0
