import logging
import os
import sys
import time

import requests
from django.core.management.base import BaseCommand

from core.models import Price
from otto.common import get_auth_token

PRODUCTS_URL = "https://api.otto.market/v2/products/"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

LOG = logging.getLogger(__name__)

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


class Command(BaseCommand):
    help = "Get price information about product."

    def handle(self, *args, **kwargs):
        """Read the price data of a single product variation."""
        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        for price in Price.objects.all():
            print(f"Fetching price for {price.sku} ...")
            url = f"{PRODUCTS_URL}/{price.sku}/prices"
            response = requests.get(url, headers=headers, timeout=60)

            response_json = response.json()
            print(response_json)
            try:
                price.vk_otto = response_json["standardPrice"]["amount"]
                price.save()
            except KeyError:
                print(f"\n>>> No price found for: {price.sku}\n")

            time.sleep(2)
