
from pprint import pprint
import requests
import os
import csv
import json
from django.utils import timezone
import time

import logging
from aboutyou.models import BatchRequest
from zalando.constants import SKU_BLACKLIST


TOKEN = os.getenv("M13_ABOUTYOU_TOKEN")
ZALANDO_FEED_PATH = os.getenv("ZALANDO_M13_FEED")

API_BASE_URL = "https://partner.aboutyou.com"
STOCK_URL = f"{API_BASE_URL}/api/v1/products/stocks"

BATCH_REQUEST_RESULT_URL = f"{API_BASE_URL}/api/v1/results/stocks"

LOG = logging.getLogger(__name__)


def download_feed():
    """Download feed from M13 shop and return list of stock."""
    if not ZALANDO_FEED_PATH:
        LOG.exception("Missing Environment Variable ZALANDO_FEED_PATH")
        raise Exception("Missing Environment Variable ZALANDO_FEED_PATH")

    try:
        response = requests.get(ZALANDO_FEED_PATH)
        decoded_content = response.content.decode("utf-8")
        cr = csv.DictReader(decoded_content.splitlines(), delimiter=";")
        return list(cr)
    except IndexError:
        LOG.exception("IndexError - is the feed available in the shop?")
        raise Exception("IndexError - is the feed available in the shop?")
    except Exception as exc:
        LOG.exception()
        raise exc


def filter_feed(original_lines: list) -> list:
    """Return list of relevant lines which hold information."""
    relevant_lines = []
    kleiner_null = []
    for line in original_lines:
        sku = line['article_number']
        quantity = line['quantity']

        if not sku:
            LOG.debug(f"SKIP (no article_number) {line}")
            continue

        if not quantity:
            LOG.debug(f"SKIP (no quantity) {line}")
            continue

        if int(quantity) < 0:
            LOG.debug(f"SKIP (quantity < 0) {line}")
            continue

        if sku in SKU_BLACKLIST:
            LOG.debug(f"SKIP (sku blacklisted) {line}")
            continue

        relevant_lines.append((sku, quantity))

    return relevant_lines


def sync():
    """Upload stock information to marketplace."""
    LOG.info("sync_stock starting ....")

    # Setup headers
    token = os.getenv("M13_ABOUTYOU_TOKEN")
    if not token:
        LOG.error("M13_ABOUTYOU_TOKEN not found")
        return
    headers = {
        "X-API-Key": token,
    }

    # Setup data
    original_feed = download_feed()
    sku_quantity_map = filter_feed(original_feed)
    LOG.info(f"len(sku_quantity_map): {len(sku_quantity_map)}")
    data = {
        "items": [{
            "sku": sku, "quantity": quantity}
            for sku, quantity in sku_quantity_map]
    }

    # Upload data
    response = requests.put(
        STOCK_URL,
        data=json.dumps(data),
        headers=headers,
        timeout=60,
    )
    if response.status_code != requests.codes.ok:
        LOG.error("stock update failed")
        LOG.error(response.json())
        return

    # Check the result - Wait until processing on AY side is done
    batch_request_id = response.json()['batchRequestId']
    br, _created = BatchRequest.objects.get_or_create(id=batch_request_id)

    for waiting_time_in_seconds in [1, 2, 4, 8, 16, 32]:
        response = requests.get(
            f"{BATCH_REQUEST_RESULT_URL}?batch_request_id={batch_request_id}",
            headers=headers,
            timeout=60,
        )
        status = response.json()['status']
        br.status = status
        br.save()

        LOG.info(f"batch_request: {br.id} status: {status}")

        if status == "completed":
            break

        LOG.info(f"waiting for {waiting_time_in_seconds} seconds")
        time.sleep(waiting_time_in_seconds)
