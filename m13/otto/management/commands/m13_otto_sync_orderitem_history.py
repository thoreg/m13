import logging
import os
import sys
import time
from pprint import pprint

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from otto.common import get_auth_token
from otto.models import Order, OrderItem, OrderItemJournal

ORDERS_URL = "https://api.otto.market/v4/orders/"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

LOG = logging.getLogger(__name__)

urllib_logger = logging.getLogger("urllib3")
urllib_logger.setLevel(logging.INFO)

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


class Command(BaseCommand):
    """..."""

    help = "Get information about otto order items."

    def _sync(self) -> None:
        """Walk through all existing orders and sync orderitems with Otto.

        GET on each order_number -> orderitem's fullfillment_status -> new Journal item

        Note: You want to truncate the table otto_orderitemjournal before you
              fire this command.
        """
        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        all_orders = Order.objects.all()
        number_of_all_orders = len(all_orders)

        for idx, order in enumerate(all_orders):
            order_number = order.marketplace_order_number

            print(f"Fetching infos for {order_number} ...")
            url = f"{ORDERS_URL}/{order_number}"
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == requests.codes.unauthorized:
                token = get_auth_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                }
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code != requests.codes.ok:
                    print(f"[{response.status_code}] Nein man - hier ist gar nichts ok")
                    response_json = response.json()
                    pprint(response_json)
                    return

            print(
                f"[{idx:05}/{number_of_all_orders}] processing order_number: {order_number}"
            )
            response_json = response.json()

            for oi in response_json["positionItems"]:
                if oi["fulfillmentStatus"] not in [
                    OrderItemJournal.OrderItemStatus.RETURNED,
                    OrderItemJournal.OrderItemStatus.SENT,
                ]:
                    continue

                if oi["fulfillmentStatus"] == OrderItemJournal.OrderItemStatus.RETURNED:
                    last_modified = oi["returnedDate"]
                    fulfillment_status = OrderItemJournal.OrderItemStatus.RETURNED
                else:
                    last_modified = oi["sentDate"]
                    fulfillment_status = OrderItemJournal.OrderItemStatus.SENT

                price = oi["itemValueGrossPrice"]["amount"]
                ean = oi["product"]["ean"]
                sku = oi["product"]["sku"]
                position_item_id = oi["positionItemId"]
                print(f"  {sku} ... ", end="")

                _oij, created = OrderItemJournal.objects.get_or_create(
                    order_number=order_number,
                    last_modified=last_modified,
                    price=price,
                    ean=ean,
                    sku=sku,
                    position_item_id=position_item_id,
                    fulfillment_status=fulfillment_status,
                )
                print(f"created: {created}", flush=True)

            time.sleep(2)

    def _wipe_n_rebuild(self):
        """Truncate journal table and rebuild it based on existing orderitems."""
        OrderItemJournal.objects.all().delete()

        all_orderitems = OrderItem.objects.select_related().all()

        for oi in all_orderitems:
            if oi.fulfillment_status not in [
                OrderItemJournal.OrderItemStatus.RETURNED,
                OrderItemJournal.OrderItemStatus.SENT,
            ]:
                print(f"skipping {oi.sku} {oi.fulfillment_status}")
                continue

            last_modified = None
            if oi.fulfillment_status == OrderItemJournal.OrderItemStatus.RETURNED:
                last_modified = oi.returned_date
                fulfillment_status = OrderItemJournal.OrderItemStatus.RETURNED
            else:
                last_modified = oi.sent_date
                fulfillment_status = OrderItemJournal.OrderItemStatus.SENT

            if not last_modified:
                last_modified = timezone.now()

            price = oi.price_in_cent / 100
            ean = oi.ean
            sku = oi.sku
            position_item_id = oi.position_item_id
            print(f"  {sku} ... ", end="")

            _oij, created = OrderItemJournal.objects.get_or_create(
                order_number=oi.order.marketplace_order_number,
                last_modified=last_modified,
                price=price,
                ean=ean,
                sku=sku,
                position_item_id=position_item_id,
                fulfillment_status=fulfillment_status,
            )
            print(f"created: {created}", flush=True)

    def add_arguments(self, parser):
        parser.add_argument("cmd_id", nargs="+", type=int)

    def handle(self, *args, **options):
        cmd = options["cmd_id"]
        if cmd[0] == 1:
            self._sync()
        elif cmd[0] == 2:
            self._wipe_n_rebuild()
        else:
            print("Unknown command - do you know what you are doing?")
            import ipdb

            ipdb.set_trace()

        return 0
