from django.core.management.base import BaseCommand

from aboutyou.services import price


class Command(BaseCommand):
    help = "Sync price (sky:quantity) with AboutYou marketplace."

    def handle(self, *args, **kwargs):
        """...."""
        price.sync()
