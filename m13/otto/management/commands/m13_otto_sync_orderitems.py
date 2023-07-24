"""Compare current content of database with the current state of Otto."""
import glob
import json
import logging
import os
import sys
import time

import requests
from django.core.management.base import BaseCommand

from otto.common import get_auth_token
from otto.models import Order

ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")


logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("otto").setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

fh = logging.FileHandler("spam.log")
fh.setLevel(logging.DEBUG)
LOG.addHandler(fh)

token = get_auth_token()

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


def check_order(json_order):
    """..."""
    order = {}
    order_number = json_order["orderNumber"]
    order[order_number] = {}
    print(f"\norder: {order_number}")

    db_order = Order.objects.get(marketplace_order_number=order_number)

    print("otto")
    order[order_number]["otto"] = {}
    for oi in json_order["positionItems"]:
        fulfillment_status = oi["fulfillmentStatus"]
        sku = oi["product"]["sku"]
        print(f"  {sku} : {fulfillment_status}")
        order[order_number]["otto"][sku] = fulfillment_status

    print("m13")
    order[order_number]["m13"] = {}
    for oi in db_order.orderitem_set.all():
        print(f"  {oi.sku} : {oi.fulfillment_status}")
        order[order_number]["m13"][oi.sku] = oi.fulfillment_status

        otto_fulfillment_status = order[order_number]["otto"][oi.sku]
        if otto_fulfillment_status != oi.fulfillment_status:
            print(
                f"FIXING - UPDATE otto_orderitem SET fulfillment_status = '{otto_fulfillment_status}' WHERE id = '{oi.id}'"
            )
            oi.fulfillment_status = otto_fulfillment_status
            oi.save()

    number_of_ois_otto = len(order[order_number]["otto"].keys())
    number_of_ois_m13 = len(order[order_number]["m13"].keys())
    if number_of_ois_otto != number_of_ois_m13:
        print(
            f"HUCH : number_of_ois_otto: {number_of_ois_otto} VS number_of_ois_m13: {number_of_ois_m13}"
        )


class Command(BaseCommand):
    help = "Import Orders from OTTO"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            type=str,
            nargs="?",
            help="Filter orders by status",
            default="PROCESSABLE",
        )
        parser.add_argument("--datum", type=str)

    def handle(self, *args, **kwargs):
        """Fetch a single order by its unique order number.."""
        check_again = []
        count = 0
        for resp_file_path in glob.glob('./responses/*.json'):
            with open(resp_file_path, "r") as f:
                content_str = f.read()
                order = json.loads(content_str)
                try:
                    # print(order['orderNumber'])
                    check_order(order)

                except KeyError:
                    check_again.append(resp_file_path)
                    # print(f"\nfile {resp_file_path} seems to have some issues")
                    # pprint(order)
                    # import ipdb; ipdb.set_trace()

                count += 1

        print(f"check again {len(check_again)}")
        print(f"order_count: {count}")

        # Download part
        # headers = {
        #     "Authorization": f"Bearer {token}",
        # }

        # orders = Order.objects.prefetch_related("orderitem_set").all()

        # order_count = orders.count()
        # count = 1
        # for order in orders:
        #     r = requests.get(
        #         f"{ORDERS_URL}/{order.marketplace_order_number}",
        #         headers=headers,
        #         timeout=60,
        #     )
        #     print(
        #         f"fetch_order() {order.marketplace_order_number} response_status_code: {r.status_code}"
        #     )
        #     with open(f"responses/{order.marketplace_order_number}.json", "w") as f:
        #         f.write(json.dumps(r.json()))

        #     count += 1
        #     print(f"progress {count}/{order_count}")
        #     time.sleep(0.5)
