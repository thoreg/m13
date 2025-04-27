


import logging
import os
import time
from pprint import pprint

import requests
from django.core.management.base import BaseCommand

from aboutyou.services import stock


AY_BASE_URL = "https://partner.aboutyou.com/api"
PRODUCTS_URL = f"{AY_BASE_URL}/v1/products"
STOCK_URL = f"{AY_BASE_URL}//v1/products/stocks"

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Get price information about product."

    def handle(self, *args, **kwargs):
        """...."""
        LOG.info("[ m13_ay_check ] started")
        stock.sync()
        # token = os.getenv("M13_ABOUTYOU_TOKEN")
        # if not token:
        #     print("M13_ABOUTYOU_TOKEN not found")
        #     return

        # headers = {
        #     "X-API-Key": token,
        # }
        # response = requests.get(
        #     PRODUCTS_URL,
        #     headers=headers,
        #     timeout=60,
        # )

        # pprint(response.json())
