from django.core.management.base import BaseCommand

from aboutyou.services import stock


class Command(BaseCommand):
    help = "Sync stock (sky:quantity) with AboutYou marketplace."

    def handle(self, *args, **kwargs):
        """...."""
        stock.sync()

