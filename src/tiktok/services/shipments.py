"""Shipment related code lives here."""

import csv
import hashlib
import hmac
import json
import logging
import os
import string
import time
from io import TextIOWrapper

import requests

from m13.lib import log as mlog
from tiktok.lib import get_access_token
from tiktok.models import Order, OrderItem, Shipment

M13_TIKTOK_APP_KEY = os.getenv("M13_TIKTOK_APP_KEY")
M13_TIKTOK_APP_SECRET = os.getenv("M13_TIKTOK_APP_SECRET")

TIKTOK_BASE_URL = "https://open-api.tiktokglobalshop.com"
TIKTOK_MARKER = "TT"
TIKTOK_ORDER_ID_LENGTH = 20


ALPHA = string.ascii_letters

LOG = logging.getLogger(__name__)


class NoAccessToken(Exception):
    pass


class NoShopCipher(Exception):
    pass


# 0. Get warehouse list
# 1. Get warehouse delivery options (by warehouse id)
# 2. Get shipping providers (by delivery option id)
SHIPPING_PROVIDER_ID = "7207996952661722922"


class ShipmentService:
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

        LOG.info(resp.json())
        return resp.json()["data"]["shops"][0]["cipher"]

    def ship_package(self, package_id: str, tracking_number: str):
        """Transmit package delivery information to TikTok."""

        endpoint = f"/fulfillment/202309/packages/{package_id}/ship"
        url = f"{TIKTOK_BASE_URL}{endpoint}"
        headers = {
            "content-type": "application/json",
            "x-tts-access-token": self.access_token,
        }

        params = {
            # order matters - keeps things sorted
            "app_key": M13_TIKTOK_APP_KEY,
            "shop_cipher": self.shop_cipher,
            "timestamp": int(time.time()),
        }

        body = {
            "handover_method": "PICKUP",
            "self_shipment": {
                "tracking_number": tracking_number,
                "shipping_provider_id": SHIPPING_PROVIDER_ID,
            },
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

        shipment, _created = Shipment.objects.get_or_create(
            tracking_number=tracking_number,
            package_id=package_id,
        )
        shipment.response_status_code = resp.status_code
        shipment.response = resp.text
        shipment.save()

        LOG.info(resp.json())


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    ss = ShipmentService()

    f = TextIOWrapper(csv_file.file, encoding="latin1")
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        # Check if row is considered to be a 'TikTok ROW'
        valid_row = False
        if (
            row
            and row[0].startswith(TIKTOK_MARKER)
            and len(row[0]) == TIKTOK_ORDER_ID_LENGTH
        ):
            valid_row = True

        if not valid_row:
            LOG.info(f"Skip non tiktok row: {row}")
            continue

        tracking_number = row[3]
        if not tracking_number:
            mlog.error(LOG, f"Tracking number not found - row: {row}")
            continue

        order_number = row[0].lstrip(TIKTOK_MARKER)
        try:
            order = Order.objects.select_related("delivery_address").get(
                tiktok_order_id=order_number
            )
        except Order.DoesNotExist:
            mlog.error(LOG, f"Order not found {order_number} - row {row}")
            continue

        orderitems = OrderItem.objects.filter(
            order=order,
        )
        for orderitem in orderitems:
            ss.ship_package(orderitem.package_id, tracking_number)
