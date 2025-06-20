from django.core.management.base import BaseCommand

from aboutyou.models import Order
from aboutyou.services import orders


class Command(BaseCommand):
    help = "Sync orders (sky:quantity) with AboutYou marketplace."

    def handle(self, *args, **kwargs):
        """...."""
        for order_status in Order.Status:
            orders.sync(order_status)
