import csv
import logging
import os

import requests

from zalando.constants import SKU_BLACKLIST

ZALANDO_FEED_PATH = os.getenv("ZALANDO_M13_FEED")
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
    for line in original_lines:
        sku = line["article_number"]
        quantity = line["quantity"]
        price = line["price"]

        if not sku:
            LOG.debug(f"SKIP (no article_number) {line}")
            continue

        if not quantity:
            LOG.debug(f"SKIP (no quantity) {line}")
            continue

        if sku in SKU_BLACKLIST:
            LOG.debug(f"SKIP (sku blacklisted) {line}")
            continue

        if int(quantity) < 0:
            quantity = 0

        relevant_lines.append((sku, quantity, price))

    return relevant_lines
