"""Create a SENT journal entry for every RETURNED where it is missing."""

from pprint import pprint

from django.core.management.base import BaseCommand

from otto.models import Order, OrderItemJournal


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_ojs = OrderItemJournal.objects.filter(
            fulfillment_status=OrderItemJournal.OrderItemStatus.RETURNED
        )

        for oj in all_ojs:
            pprint(oj)
            if not oj.sent_exist:
                order = Order.objects.get(marketplace_order_number=oj.order_number)
                print(f"  order_date: {order.order_date}")
                _oij, created = OrderItemJournal.objects.get_or_create(
                    order_number=oj.order_number,
                    last_modified=order.order_date,
                    price=oj.price,
                    ean=oj.ean,
                    sku=oj.sku,
                    position_item_id=oj.position_item_id,
                    fulfillment_status=OrderItemJournal.OrderItemStatus.SENT,
                )
                print(f"created: {created}", flush=True)
