import json
import os
import pprint
import sys
from functools import reduce
from pprint import pformat

import requests
from django.core.management.base import BaseCommand, CommandError
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth

from otto.common import get_auth_token
from otto.models import Address, Order, OrderItem
from otto.services.orders import fetch_orders, save_orders

TOKEN_URL = "https://api.otto.market/v1/token"
ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

token = ""

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


def safenget(dct, key, default=None):
    """Get nested dict items safely."""
    try:
        return reduce(dict.__getitem__, key.split('.'), dct)
    # KeyError is for key not available, TypeError is for nested item not
    # subscriptable, e.g. getting a.b.c, but a.b is None or an int.
    except (KeyError, TypeError):
        return default


class Command(BaseCommand):
    help = "Import Orders from OTTO"

    def add_arguments(self , parser):
        parser.add_argument(
            '--status', type=str, nargs='?',
            help='Filter orders by status', default='PROCESSABLE')
        parser.add_argument('--datum', type=str)

    def handle(self, *args, **kwargs):
        """Pull (fetch+merge) orders from marketplace."""
        status = kwargs.get('status')
        datum = kwargs.get('datum')

        token = get_auth_token()
        orders = fetch_orders(token, status, datum)
        save_orders(orders)
