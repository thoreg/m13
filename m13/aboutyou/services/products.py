import logging
import os

import requests

from aboutyou.models import Product

from .common import API_BASE_URL

LOG = logging.getLogger(__name__)

PRODUCTS_URL = f"{API_BASE_URL}/api/v1/products/"


def get_product_title(sku: str) -> str:
    """AY product titles follow their own rules.

    Which means special handling aka 'extra Locke'.

    """
    token = os.getenv("M13_ABOUTYOU_TOKEN")
    if not token:
        LOG.error("M13_ABOUTYOU_TOKEN not found")
        return

    headers = {
        "X-API-Key": token,
    }

    title = ""
    try:
        product = Product.objects.get(sku=sku)
        title = product.product_title
    except Product.DoesNotExist:
        LOG.info(f"syncing product title for: {sku}")
        response = requests.get(
            f"{PRODUCTS_URL}?sku={sku}",
            headers=headers,
            timeout=60,
        )
        if response.status_code != requests.codes.ok:
            LOG.error(f"fetching product ({sku}) failed")
            LOG.error(response.json())
            return "fetching_error"

        if len(response.json()["items"]):
            LOG.error(f"fetching product ({sku}) unexpected response")
            LOG.error(response.json())
            return "items_error"

        title = response.json()["items"][0]["name"]
        Product.objects.get_or_create(sku=sku, defaults={"product_title": title})

    return title
