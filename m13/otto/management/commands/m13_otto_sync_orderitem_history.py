import logging
import os
import sys
import time
from datetime import date

import requests
from dateutil.relativedelta import relativedelta
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
    LOG.info("\nyou need to define username and password\n")
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
        # twelve_months_ago = date.today() + relativedelta(months=-12)
        six_months_ago = date.today() + relativedelta(months=-6)
        # OrderItemJournal.objects.all().delete()
        # OrderItemJournal.objects.filter(order_date__gt=twelve_months_ago)
        OrderItemJournal.objects.filter(order_date__gt=six_months_ago).delete()

        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        # all_orders = Order.objects.all()
        # all_orders = Order.objects.filter(order_date__gt=twelve_months_ago)
        all_orders = Order.objects.filter(order_date__gt=six_months_ago)

        # all_orders = Order.objects.all()[1203:]
        # all_orders = Order.objects.filter(order_date__gt="2024-01-01")
        # all_orders = Order.objects.filter(marketplace_order_number="cbn4kqmhyn")
        number_of_all_orders = len(all_orders)

        for idx, order in enumerate(all_orders):
            order_number = order.marketplace_order_number
            order_date = order.order_date

            LOG.info(f"Fetching infos for {order_number} ... ")
            url = f"{ORDERS_URL}/{order_number}"
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == requests.codes.unauthorized:
                token = get_auth_token()
                headers = {
                    "Authorization": f"Bearer {token}",
                }
                response = requests.get(url, headers=headers, timeout=60)
                if response.status_code != requests.codes.ok:
                    LOG.info(
                        f"[{response.status_code}] Nein man - hier ist gar nichts ok"
                    )
                    response_json = response.json()
                    LOG.info(response_json)
                    return
            LOG.info(f"{response.status_code}")

            LOG.info(
                f"[{idx:05}/{number_of_all_orders}] processing order_number: {order_number}"
            )
            try:
                response_json = response.json()
            except:
                LOG.error(response)
                continue

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
                LOG.info(f"  {sku} ... ")

                _oij, created = OrderItemJournal.objects.get_or_create(
                    order_number=order_number,
                    last_modified=last_modified,
                    price=price,
                    ean=ean,
                    sku=sku,
                    position_item_id=position_item_id,
                    fulfillment_status=fulfillment_status,
                    order_date=order_date,
                )
                LOG.info(f"created: {created}")

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
                LOG.info(f"skipping {oi.sku} {oi.fulfillment_status}")
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
            LOG.info(f"  {sku} ... ")

            _oij, created = OrderItemJournal.objects.get_or_create(
                order_number=oi.order.marketplace_order_number,
                last_modified=last_modified,
                price=price,
                ean=ean,
                sku=sku,
                position_item_id=position_item_id,
                fulfillment_status=fulfillment_status,
            )
            LOG.info(f"created: {created}")

    def add_arguments(self, parser):
        parser.add_argument("cmd_id", nargs="+", type=int)

    def handle(self, *args, **options):
        cmd = options["cmd_id"]
        if cmd[0] == 1:
            self._sync()
        elif cmd[0] == 2:
            self._wipe_n_rebuild()
        else:
            LOG.info("Unknown command - do you know what you are doing?")
            import ipdb

            ipdb.set_trace()

        return 0
