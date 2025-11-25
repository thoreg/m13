import json
import logging
import os
import time

import requests

from aboutyou.models import BatchRequest
from m13.lib.common import chunk
from m13.lib.email import send_error_as_email

from .common import API_BASE_URL, download_feed, filter_feed

STOCK_URL = f"{API_BASE_URL}/api/v1/products/stocks"
BATCH_REQUEST_RESULT_URL = f"{API_BASE_URL}/api/v1/results/stocks"

LOG = logging.getLogger(__name__)

MAX_CHUNK_SIZE = 500


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
    sku_quantity_price_map = filter_feed(original_feed)
    LOG.info(f"len(sku_quantity_price_map) in total: {len(sku_quantity_price_map)}")

    for sku_quantity_price_map_chunk in chunk(sku_quantity_price_map, MAX_CHUNK_SIZE):
        data = {
            "items": [
                {"sku": sku, "quantity": quantity}
                for sku, quantity, _price in sku_quantity_price_map_chunk
            ]
        }

        # Upload data
        response = requests.put(
            STOCK_URL,
            data=json.dumps(data),
            headers=headers,
            timeout=60,
        )
        if response.status_code != requests.codes.ok:
            subj = "ay - stock update failed"
            try:
                msg = response.json()
                LOG.error(subj)
                LOG.error(msg)
                send_error_as_email(subj, msg)
            except Exception:
                send_error_as_email(subj, response.text)

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
