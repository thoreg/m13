import csv
import json
import logging
import os
import time
from pprint import pprint

import requests

from aboutyou.models import Address, BatchRequest, Order, OrderItem

from .common import API_BASE_URL, download_feed, filter_feed

ORDERS_URL = f"{API_BASE_URL}/api/v1/orders/"
BATCH_REQUEST_RESULT_URL = f"{API_BASE_URL}/api/v1/results/stocks"

LOG = logging.getLogger(__name__)


def sync():
    LOG.info("sync_orders starting ....")

    # Setup headers
    token = os.getenv("M13_ABOUTYOU_TOKEN")
    if not token:
        LOG.error("M13_ABOUTYOU_TOKEN not found")
        return
    headers = {
        "X-API-Key": token,
    }
    response = requests.get(
        f"{ORDERS_URL}",
        headers=headers,
        timeout=60,
    )
    if response.status_code != requests.codes.ok:
        LOG.error("fetching orders failed")
        LOG.error(response.json())
        return

    for entry in response.json()["items"]:

        marketplace_order_id = entry.get("order_number")
        status = entry.get("status")

        delivery_address, _created = Address.objects.get_or_create(
            addition=entry.get("shipping_additional"),
            city=entry.get("shipping_city"),
            country_code=entry.get("shipping_country_code"),
            first_name=entry.get("shipping_recipient_first_name"),
            last_name=entry.get("shipping_recipient_last_name"),
            street=entry.get("shipping_street"),
            zip_code=entry.get("shipping_zip_code"),
        )
        invoice_address, _created = Address.objects.get_or_create(
            addition=entry.get("billing_additional"),
            city=entry.get("billing_city"),
            country_code=entry.get("billing_country_code"),
            first_name=entry.get("billing_recipient_first_name"),
            last_name=entry.get("billing_recipient_last_name"),
            street=entry.get("billing_street"),
            zip_code=entry.get("billing_zip_code"),
        )

        order, created = Order.objects.get_or_create(
            marketplace_order_id=marketplace_order_id,
            defaults={
                "delivery_address": delivery_address,
                "invoice_address": invoice_address,
                "order_date": entry.get("created_at"),
                "status": Order.Status(status),
            },
        )
        if created:
            LOG.info(f"Order {marketplace_order_id} imported")
        else:
            LOG.info(f"Order {marketplace_order_id} already known")
            order.status = Order.Status(status)
            order.save()

        for oi in entry.get("order_items"):
            fulfillment_status = oi["status"]
            position_item_id = oi["id"]
            sku = oi["sku"]

            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                position_item_id=position_item_id,
                defaults={
                    "fulfillment_status": fulfillment_status,
                    "price_in_cent": oi["price_with_tax"],
                    "sku": sku,
                    "vat_rate": oi["vat"],
                },
            )
            if not created:
                order_item.fulfillment_status = fulfillment_status
                order_item.save()
