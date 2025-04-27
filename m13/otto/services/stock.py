"""Upload stock information to OTTO."""

import json
import logging
import os
import time
from datetime import datetime

import requests

from m13.lib.common import chunk
from otto.common import get_auth_token

LOG = logging.getLogger(__name__)

M13_OTTO_FEED_URL = os.getenv("M13_OTTO_FEED_URL")

OTTO_QUANTITIES_URL = "https://api.otto.market/v1/availability/quantities"
MAX_CHUNK_SIZE = 200


def sync_stock():
    """Get the feed and upload stock information.

    Load 200 items to the payload and do the post request

    """

    def _renew_token():
        token = get_auth_token()
        LOG.info(f"get fresh token: {token}")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        return headers

    feed = requests.get(M13_OTTO_FEED_URL, timeout=60)
    stock = json.loads(feed.content)

    headers = _renew_token()

    for _chunk in chunk(stock, MAX_CHUNK_SIZE):
        for product in _chunk:
            time.sleep(2)
            payload = []

            sku = product["sku"]
            quantity = product["quantity"]

            if quantity == "" or quantity is None:
                LOG.info(f"Skip {sku} because of no quantity")
                continue

            payload.append({"quantity": quantity, "sku": sku})

            resp = requests.post(
                f"{OTTO_QUANTITIES_URL}", headers=headers, json=payload, timeout=60
            )

            if resp.status_code == requests.codes.unauthorized:
                headers = _renew_token()
                resp = requests.post(
                    f"{OTTO_QUANTITIES_URL}", headers=headers, json=payload, timeout=60
                )
                if resp.status_code == requests.codes.ok:
                    LOG.info(f"2nd try - sku: {sku} qu: {quantity} updated")
                else:
                    LOG.error(f"update sku: {sku} qu: {quantity} failed")
                    LOG.error(f"status_code: {resp.status_code}")
                    LOG.error(resp.json())
                    continue

            elif resp.status_code == requests.codes.ok:
                LOG.info(f"sku: {sku} qu: {quantity} updated")

            else:
                LOG.error(f"unexpected status_code: {resp.status_code}")
                LOG.error(resp.json())
