import logging

from django.core.management.base import BaseCommand

from tiktok.models import Order
from tiktok.services.orders import OrderService

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Get orders from marketplace."""
        order_service = OrderService()
        order_status_list = [choice[0] for choice in Order.Status.choices]
        # order_status_list = ["AWAITING_SHIPMENT", "CANCELLED"]

        for order_status in order_status_list:
            order_service.get_orders(Order.Status(order_status))
