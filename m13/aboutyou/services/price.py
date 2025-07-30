import json
import logging
import os
import time

import requests

from aboutyou.models import BatchRequest
from core.models import Price
from m13.lib import log as mlog
from m13.lib.email import send_error_as_email
from zalando.models import PriceTool

from .common import API_BASE_URL, download_feed, filter_feed

PRICE_URL = f"{API_BASE_URL}/api/v1/products/prices"
BATCH_REQUEST_RESULT_URL = f"{API_BASE_URL}/api/v1/results/prices"

LOG = logging.getLogger(__name__)


PRICES = [
    14.95,
    17.95,
    19.95,
    24.95,
    27.95,
    29.95,
    34.95,
    37.95,
    39.95,
    44.95,
    47.95,
    49.95,
    54.95,
    59.95,
    64.95,
    69.95,
    74.95,
    79.95,
    84.95,
    89.95,
    99.95,
    104.95,
    109.95,
    114.95,
    119.95,
    124.95,
    129.95,
    132.95,
    134.95,
    139.95,
    144.95,
    149.95,
    154.95,
    159.95,
    164.95,
    169.95,
    174.95,
    179.95,
    184.95,
    189.95,
    199.95,
]

SHIPPING_FEE = 3.95


def _get_price(price, factor) -> str:
    """Return beautiful price after factor was applied."""
    price = round(price * factor, 2) + SHIPPING_FEE

    while True:
        # print(price)
        price = round(price + 0.01, 2)
        if price in PRICES:
            return str(price)

        if price > 200:
            # This should never happen
            return "ERROR"


def get_z_factor():
    price_tool = PriceTool.objects.get(active=True)
    if not price_tool:
        raise Exception("No Base Price Found")

    return float(price_tool.z_factor)


def sync():
    """Upload price information to marketplace."""
    LOG.info("sync_price starting ....")

    # Setup headers
    token = os.getenv("M13_ABOUTYOU_TOKEN")
    if not token:
        LOG.error("M13_ABOUTYOU_TOKEN not found")
        return
    headers = {
        "X-API-Key": token,
    }

    try:
        factor = get_z_factor()
    except PriceTool.DoesNotExist:
        mlog.error(LOG, "No price factor found")
        raise Exception("No price factor found")

    # Setup data
    original_feed = download_feed()
    sku_quantity_price_map = filter_feed(original_feed)
    LOG.info(f"len(sku_quantity_price_map): {len(sku_quantity_price_map)}")

    items = []
    for sku, _quantity, old_price in sku_quantity_price_map:
        try:
            core_price = Price.objects.get(sku__iexact=sku, vk_aboutyou__isnull=False)
            price = str(core_price.vk_aboutyou)
            LOG.debug(f"{sku} - price via overwrite: {price}")

        except Price.DoesNotExist:
            _price = float(old_price.replace(",", "."))
            LOG.debug(f"_get_price() for {sku} _price: {_price}")
            price = _get_price(_price, factor)
            LOG.debug(f"{sku} - price via _get_price() : {price}")

        LOG.debug(f"{sku}: {price} -> {price}")
        items.append(
            {
                "sku": sku,
                "price": {
                    "country_code": "DE",
                    "retail_price": float(price),
                },
            }
        )

    data = {"items": items}

    # Upload data
    response = requests.put(
        PRICE_URL,
        data=json.dumps(data),
        headers=headers,
        timeout=60,
    )
    if response.status_code != requests.codes.ok:
        subj = "ay - price update failed"
        msg = response.json()
        LOG.error(subj)
        LOG.error(msg)

        send_error_as_email(subj, msg)
        return

    # Check the result - Wait until processing on AY side is done
    batch_request_id = response.json()["batchRequestId"]
    br, _created = BatchRequest.objects.get_or_create(id=batch_request_id)

    for waiting_time_in_seconds in [1, 2, 4, 8, 16, 32]:
        response = requests.get(
            f"{BATCH_REQUEST_RESULT_URL}?batch_request_id={batch_request_id}",
            headers=headers,
            timeout=60,
        )
        status = response.json()["status"]
        br.status = status
        br.save()

        LOG.info(f"batch_request: {br.id} status: {status}")

        if status == "completed":
            break

        LOG.info(f"waiting for {waiting_time_in_seconds} seconds")
        time.sleep(waiting_time_in_seconds)
