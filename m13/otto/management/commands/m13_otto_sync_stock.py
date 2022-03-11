from django.core.management.base import BaseCommand

from otto.services.stock import sync_stock


class Command(BaseCommand):
    help = "...."

    def handle(self, *args, **kwargs):
        """..."""
        sync_stock()