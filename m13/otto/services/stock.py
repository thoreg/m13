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

OTTO_QUANTITIES_URL = "https://api.otto.market/v2/quantities"

MAX_CHUNK_SIZE = 100


def sync_stock():
    """Get the feed and upload stock information."""

    def _renew_token():
        token = get_auth_token()
        LOG.info(f"get fresh token: {token}")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        return headers

    feed = requests.get(M13_OTTO_FEED_URL, timeout=60)
    stock = json.loads(feed.content)

    last_modified = f"{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"

    headers = _renew_token()
    for _chunk in chunk(stock, MAX_CHUNK_SIZE):
        LOG.info(len(_chunk))

        for product in _chunk:
            time.sleep(2)
            # LOG.info(product)
            payload = []
            sku = product["sku"]
            quantity = product["quantity"]
            if quantity == "" or quantity is None:
                LOG.info(f"Skip {sku} because of no quantity")
                continue

            payload.append(
                {"lastModified": last_modified, "quantity": quantity, "sku": sku}
            )
            resp = requests.post(
                f"{OTTO_QUANTITIES_URL}", headers=headers, json=payload, timeout=60
            )

            if resp.status_code == requests.codes.unauthorized:
                headers = _renew_token()
                resp = requests.post(
                    f"{OTTO_QUANTITIES_URL}", headers=headers, json=payload, timeout=60
                )
                if resp.status_code != requests.codes.ok:
                    LOG.error(f"update sku: {sku} qu: {quantity} failed")
                    LOG.error(f"status_code: {resp.status_code}")
                    LOG.error(resp.json())
                    continue

            elif resp.status_code == requests.codes.ok:
                LOG.info(f"updated - sku: {sku} quantity : {quantity} - ok")

            else:
                LOG.error(f"unexpected status_code: {resp.status_code}")
                LOG.error(resp.json())
