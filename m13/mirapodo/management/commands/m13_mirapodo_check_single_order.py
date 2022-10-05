
from django.core.management.base import BaseCommand

from mirapodo.services.orders import fetch_order_by_id


class Command(BaseCommand):
    help = "Get the information for a specific order."

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Define an order id')

    def handle(self, *args, **kwargs):
        """..."""
        order_id = kwargs.get('id')
        if not order_id:
            self.stdout.write(self.style.ERROR("Please provide order_id via e.g. '-i 405'"))
            return
        fetch_order_by_id(kwargs['id'])
