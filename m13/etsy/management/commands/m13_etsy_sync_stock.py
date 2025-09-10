from django.core.management.base import BaseCommand

from etsy.services import stock


class Command(BaseCommand):
    help = "Sync stock (sky:quantity) with AboutYou marketplace."

    def handle(self, *args, **kwargs):
        """...."""
        ess = stock.EtsyStockSync()
        ess.sync_active_listings()
        ess.sync_stock()
