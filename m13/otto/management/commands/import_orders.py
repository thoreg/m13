import logging
import os
import sys
from functools import reduce

from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from otto.common import get_auth_token
from otto.services.orders import fetch_next_slice, fetch_orders_by_status, save_orders

TOKEN_URL = "https://api.otto.market/v1/token"
ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

LOG = logging.getLogger(__name__)

token = ""

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


def safenget(dct, key, default=None):
    """Get nested dict items safely."""
    try:
        return reduce(dict.__getitem__, key.split("."), dct)
    # KeyError is for key not available, TypeError is for nested item not
    # subscriptable, e.g. getting a.b.c, but a.b is None or an int.
    except (KeyError, TypeError):
        return default


def get_next_slice(token, orders):
    LOG.info(f"paginated response - href: {orders['links'][0]['href']}")
    orders = fetch_next_slice(token, orders["links"][0]["href"])
    save_orders(orders)
    if "links" in orders:
        get_next_slice(token, orders)


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

    @monitor
    def handle(self, *args, **kwargs):
        """Pull (fetch+merge) orders from marketplace."""
        status = kwargs.get("status")
        datum = kwargs.get("datum")

        token = get_auth_token()
        orders = fetch_orders_by_status(token, status, datum)
        save_orders(orders)

        if "links" in orders:
            get_next_slice(token, orders)
