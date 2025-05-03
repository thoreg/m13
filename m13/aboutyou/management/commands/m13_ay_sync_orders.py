from django.core.management.base import BaseCommand

from aboutyou.services import orders


class Command(BaseCommand):
    help = "Sync orders (sky:quantity) with AboutYou marketplace."

    def handle(self, *args, **kwargs):
        """...."""
        orders.sync()
