"""Tiktok stock sync service."""

import hashlib
import hmac
import json
import logging
import os
import time
from pprint import pformat, pprint

import requests

from tiktok.lib import get_access_token
from tiktok.models import Product

M13_TIKTOK_APP_KEY = os.getenv("M13_TIKTOK_APP_KEY")
M13_TIKTOK_APP_SECRET = os.getenv("M13_TIKTOK_APP_SECRET")

TIKTOK_BASE_URL = "https://open-api.tiktokglobalshop.com"

MAX_PAGE_SIZE = 5

LOG = logging.getLogger(__name__)


class NoAccessToken(Exception):
    pass


class NoShopCipher(Exception):
    pass


class StockService:
    acccess_token: str | None = None
    shop_cipher: str | None = None

    def __init__(self):
        self.access_token = get_access_token()
        if not self.access_token:
            LOG.error("no access token received")
            raise NoAccessToken
        LOG.info(f"access_token: {self.access_token}")

        self.shop_cipher = self.get_shop_cipher()
        if not self.shop_cipher:
            LOG.error("no shop cipher received")
            raise NoShopCipher
        LOG.info(f"shop_cipher: {self.shop_cipher}")

    def get_shop_cipher(self) -> str | None:
        """Return the shop cipher."""

        TIKTOK_GET_AUTHORIZED_SHOPS = "/authorization/202309/shops"
        url = f"{TIKTOK_BASE_URL}{TIKTOK_GET_AUTHORIZED_SHOPS}"
        headers = {
            "content-type": "application/json",
            "x-tts-access-token": self.access_token,
        }

        params = {"app_key": M13_TIKTOK_APP_KEY, "timestamp": int(time.time())}

        sign_string = f"{M13_TIKTOK_APP_SECRET}{TIKTOK_GET_AUTHORIZED_SHOPS}"
        for k, v in sorted(params.items()):
            sign_string += f"{k}{v}"
        sign_string += f"{M13_TIKTOK_APP_SECRET}"

        sign = hmac.new(
            f"{M13_TIKTOK_APP_SECRET}".encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()
        params["sign"] = sign

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != requests.codes.ok:
            LOG.error(resp)
            return

        if len(resp.json()["data"]["shops"]) > 1:
            LOG.error("Houston we received more than one shop")
            LOG.error("Please check this manually")
            LOG.error(resp.json())
            return

        LOG.info(pformat(resp.json()))
        return resp.json()["data"]["shops"][0]["cipher"]

    def get_products(self, refresh=False, next_page_token=None):
        """Receive all product information from the shop."""

        if refresh:
            Product.objects.all().delete()

        # endpoint = "/product/202502/products/search"
        endpoint = "/product/202309/products/search"
        url = f"{TIKTOK_BASE_URL}{endpoint}"
        headers = {
            "content-type": "application/json",
            "x-tts-access-token": self.access_token,
        }

        params = {
            # order matters - keeps things sorted
            "app_key": M13_TIKTOK_APP_KEY,
            "page_size": MAX_PAGE_SIZE,
            "shop_cipher": self.shop_cipher,
            "timestamp": int(time.time()),
        }

        if next_page_token:
            params["page_token"] = next_page_token

        body = """{
    "status": "ACTIVATE",
    "listing_quality_tier": "GOOD"
}"""

        sign_string = f"{M13_TIKTOK_APP_SECRET}{endpoint}"
        for k, v in sorted(params.items()):
            sign_string += f"{k}{v}"

        sign_string += body
        sign_string += f"{M13_TIKTOK_APP_SECRET}"

        sign = hmac.new(
            f"{M13_TIKTOK_APP_SECRET}".encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()
        params["sign"] = sign

        resp = requests.post(url, headers=headers, params=params, data=body)
        if resp.status_code != requests.codes.ok:
            LOG.error(resp.json())
            return

        pprint(resp.json())

        resp = resp.json()
        next_page_token = resp["data"]["next_page_token"]

        for product in resp["data"]["products"]:
            tiktok_product_id = product["id"]
            for sku in product["skus"]:
                seller_sku = sku["seller_sku"]
                for inventory in sku["inventory"]:
                    warehouse_id = inventory["warehouse_id"]
                    _obj, created = Product.objects.get_or_create(
                        seller_sku=seller_sku,
                        sku_id=sku["id"],
                        status=product["status"],
                        tiktok_product_id=tiktok_product_id,
                        title=product["title"],
                        warehouse_id=warehouse_id,
                    )
                    if created:
                        LOG.info(f"created {tiktok_product_id} for sku {seller_sku}")
                    else:
                        LOG.info(
                            f"sku {seller_sku} already known as {tiktok_product_id}"
                        )

        LOG.info(f'Houston we got {len(resp["data"]["products"])} products')

        if next_page_token:
            LOG.info("Houston we got a next_page_token - going for another round")
            self.get_products(next_page_token=next_page_token)

    def update_inventory(self, sku: str, quantity: int):
        """Update inventory information per sku_id.

        The SKU ID generated by TikTok Shop. One product can contain multiple SKU IDs.

        Note:
        - The SKU ID must belong to a product with the ACTIVATE status.
        - If you are updating multiple SKUs, all the SKU IDs must belong to the same product.

        """
        try:
            product = Product.objects.get(seller_sku=sku)
        except Product.DoesNotExist:
            LOG.error(f"product not found in db - sku {sku}")
            return

        endpoint = (
            f"/product/202309/products/{product.tiktok_product_id}/inventory/update"
        )
        url = f"{TIKTOK_BASE_URL}{endpoint}"

        headers = {
            "content-type": "application/json",
            "x-tts-access-token": self.access_token,
        }
        params = {
            # order matters - keeps things sorted
            "app_key": M13_TIKTOK_APP_KEY,
            "page_size": MAX_PAGE_SIZE,
            "shop_cipher": self.shop_cipher,
            "timestamp": int(time.time()),
        }
        body = {
            "skus": [
                {
                    "id": product.sku_id,
                    "inventory": [
                        {
                            "warehouse_id": product.warehouse_id,
                            "quantity": quantity,
                        }
                    ],
                }
            ]
        }
        body = json.dumps(body)

        sign_string = f"{M13_TIKTOK_APP_SECRET}{endpoint}"
        for k, v in sorted(params.items()):
            sign_string += f"{k}{v}"

        sign_string += body
        sign_string += f"{M13_TIKTOK_APP_SECRET}"

        sign = hmac.new(
            f"{M13_TIKTOK_APP_SECRET}".encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()
        params["sign"] = sign

        resp = requests.post(url, headers=headers, params=params, data=body)
        if resp.status_code != requests.codes.ok:
            LOG.error(resp.json())
            return

        pprint(resp.json())
