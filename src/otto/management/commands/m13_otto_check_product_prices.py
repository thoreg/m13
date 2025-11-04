import logging
import time
from pprint import pprint

import requests
from django.core.management.base import BaseCommand

from core.models import Price
from otto.common import get_auth_token

PRODUCTS_URL = "https://api.otto.market/v3/products/prices"

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Get price information about product."

    def handle(self, *args, **kwargs):
        """Read the price data of a single product variation."""
        token = get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        for price in Price.objects.all()[:200]:
            print(f"Fetching price for {price.sku} ...")
            url = f"{PRODUCTS_URL}"
            params = {"sku": price.sku}
            response = requests.get(
                url,
                headers=headers,
                timeout=60,
                params=params,
            )

            response_json = response.json()
            pprint(response_json)
            # try:
            #     price.vk_otto = response_json["standardPrice"]["amount"]
            #     price.save()
            # except KeyError:
            #     print(f"\n>>> No price found for: {price.sku}\n")

            time.sleep(2)

        return 0
