"""Tiktok stock sync service."""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime
from pprint import pprint

import requests

from tiktok.lib import get_access_token
from tiktok.models import Address, Order, OrderItem

M13_TIKTOK_APP_KEY = os.getenv("M13_TIKTOK_APP_KEY")
M13_TIKTOK_APP_SECRET = os.getenv("M13_TIKTOK_APP_SECRET")

TIKTOK_BASE_URL = "https://open-api.tiktokglobalshop.com"

MAX_PAGE_SIZE = 5

LOG = logging.getLogger(__name__)


class NoAccessToken(Exception):
    pass


class NoShopCipher(Exception):
    pass


class OrderService:
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

        # from pprint import pformat
        # LOG.info(pformat(resp.json()))
        return resp.json()["data"]["shops"][0]["cipher"]

    def get_orders(self, order_status=Order.Status.UNPAID, next_page_token=None):
        """Receive orders from marketplace."""
        LOG.info(f"order_status: {order_status}")

        endpoint = "/order/202309/orders/search"
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

        body = {
            "order_status": order_status,
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

        resp = resp.json()

        if resp["data"]["total_count"] == 0:
            LOG.info(f"No orders with status {order_status}")
            return

        next_page_token = resp["data"]["next_page_token"]

        for order in resp["data"]["orders"]:
            pprint(order)

            #
            # Address
            #
            ra = order["recipient_address"]
            address_obj, created = Address.objects.get_or_create(
                city=ra["district_info"][2]["address_name"],
                country_code=ra["region_code"],
                email=order["buyer_email"],
                first_name=ra["first_name"],
                full_address=ra["full_address"],
                last_name=ra["last_name"],
                street=f"{ra['address_line1']} {ra['address_line2']}".strip(),
                zip_code=ra["postal_code"],
            )
            if created:
                LOG.info(
                    f"    address: {address_obj.first_name} {address_obj.last_name} created"
                )
            else:
                LOG.info(
                    f"    address: {address_obj.first_name} {address_obj.last_name} known"
                )

            #
            # Order
            #
            order_obj, created = Order.objects.get_or_create(
                tiktok_order_id=order["id"],
                defaults=dict(
                    buyer_email=order["buyer_email"],
                    create_time=datetime.fromtimestamp(order["create_time"]),
                    delivery_address=address_obj,
                    delivery_fee=order["payment"]["original_shipping_fee"],
                    rts_sla_time=datetime.fromtimestamp(order["rts_sla_time"]),
                    status=order["status"],
                ),
            )
            if created:
                LOG.info(f"order: {order_obj.id} created - status: {order_status}")
            else:
                LOG.info(f"order: {order_obj.id} known - status: {order_status}")
                if order_obj.status != order_status:
                    LOG.info(
                        f"o_id: {order_obj.id} status {order_obj.status} -> {order_status}"
                    )
                    order_obj.status = order_status
                    order_obj.save()

            #
            # OrderItems
            #
            for oi in order["line_items"]:
                status = oi["display_status"]
                oi_obj, created = OrderItem.objects.get_or_create(
                    tiktok_orderitem_id=oi["id"],
                    defaults=dict(
                        order=order_obj,
                        package_id=oi["package_id"],
                        price=oi["sale_price"],
                        sku=oi["seller_sku"],
                        status=status,
                        tiktok_product_name=oi["product_name"],
                        tiktok_sku_id=oi["sku_id"],
                    ),
                )
                if created:
                    LOG.info(f"    oid: {oi_obj.id} created - status: {status}")
                else:
                    LOG.info(f"    oid: {oi_obj.id} known - status: {status}")

                    if oi_obj.status != status:
                        LOG.info(
                            f"oi_obj.id: {oi_obj.id} status {oi_obj.status} -> {status}"
                        )
                        oi_obj.status = status
                        oi_obj.save()

        LOG.info(
            f'order_status: {order_status}: {len(resp["data"]["orders"])} orders received'
        )

        if next_page_token:
            LOG.info("Houston we got a next_page_token - going for another round")
            self.get_orders(next_page_token=next_page_token)
