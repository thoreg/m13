"""irisOne order import service.

Fetches orders from GET /v1/orders and persists them locally.
Already-known orders (by booking_id) are skipped.
"""

import logging
import os

import requests
from django.utils.dateparse import parse_datetime

from irisone.models import Order, OrderLine

LOG = logging.getLogger(__name__)

IRISONE_API_KEY = os.getenv("IRISONE_API_KEY", "")
IRISONE_API_BASE_URL = os.getenv(
    "IRISONE_API_BASE_URL", "https://api.io-staging.irisone.io/erp"
)

HEADERS = {"x-api-key": IRISONE_API_KEY, "user-agent": "manufaktur13"}


class IrisOneOrderException(Exception):
    pass


def _fetch_orders_page(status=None, page=1):
    """Fetch one page of orders from the irisOne API."""
    if not IRISONE_API_KEY:
        raise IrisOneOrderException("Missing environment variable IRISONE_API_KEY")

    params = {"page": page}
    if status:
        params["status"] = status

    url = f"{IRISONE_API_BASE_URL}/v1/orders"
    LOG.info(f"GET {url}")
    response = requests.get(url, headers=HEADERS, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def _upsert_order(data):
    """Create or update a single order record. Returns (order, created)."""
    order, created = Order.objects.get_or_create(
        booking_id=data["booking_id"],
        defaults={
            "order_id": data["order_id"],
            "marketplace_name": data.get("marketplace_name", ""),
            "marketplace_detail": data.get("marketplace_detail", ""),
            "marketplace_order_id_1": data.get("marketplace_order_id_1", ""),
            "marketplace_order_id_2": data.get("marketplace_order_id_2") or "",
            "order_date": parse_datetime(data["order_date"]),
            "currency": data.get("currency", "EUR"),
            "buyer_country": data.get("buyer_country", ""),
            "status": data.get("status", Order.Status.PENDING),
            "exported": data.get("exported", False),
            "origin_labels": data.get("origin_labels") or "",
            "origin_documents": data.get("origin_documents") or "",
            "origin_invoices": data.get("origin_invoices") or "",
        },
    )

    if not created:
        # Update status and exported flag in case they changed
        updated = False
        new_status = data.get("status", order.status)
        if order.status != new_status:
            order.status = new_status
            updated = True
        if order.exported != data.get("exported", order.exported):
            order.exported = data.get("exported", order.exported)
            updated = True
        if updated:
            order.save(update_fields=["status", "exported"])

    return order, created


def _upsert_lines(order, lines_data):
    """Create order lines that do not yet exist."""
    created_count = 0
    for line in lines_data:
        _, created = OrderLine.objects.get_or_create(
            line_id=line["line_id"],
            defaults={
                "order": order,
                "item_id": line.get("item_id", 0),
                "line_identifier": line.get("line_identifier", ""),
                "marketplace_sku": line.get("marketplace_sku", ""),
                "article_number": _resolve_article_number(line),
                "price": line.get("price", ""),
                "price_net": line.get("price_net", ""),
                "vat": line.get("vat", ""),
                "status": line.get("status", OrderLine.Status.PENDING),
            },
        )
        if created:
            created_count += 1
    return created_count


def _resolve_article_number(line):
    """Extract article number from erp_additions or marketplace_sku fallback."""
    erp = line.get("erp_additions") or {}
    return erp.get("erp_id", line.get("marketplace_sku", ""))


def import_orders(status=None):
    """Fetch all pages of orders from irisOne and persist new ones.

    Args:
        status: optional filter — 'pending', 'opened', or 'fulfilled'

    Returns:
        dict with counts: orders_created, orders_updated, lines_created
    """
    counts = {"orders_created": 0, "orders_updated": 0, "lines_created": 0}
    page = 1

    while True:
        payload = _fetch_orders_page(status=status, page=page)
        orders_data = payload.get("data", [])
        meta = payload.get("meta", {})

        LOG.info(f"Page {page}/{meta.get('last_page', '?')}: {len(orders_data)} orders")

        for order_data in orders_data:
            order, created = _upsert_order(order_data)
            if created:
                counts["orders_created"] += 1
                LOG.info(f"New order: booking_id={order.booking_id}")
            else:
                counts["orders_updated"] += 1

            lines_created = _upsert_lines(order, order_data.get("lines", []))
            counts["lines_created"] += lines_created

        if page >= meta.get("last_page", 1):
            break
        page += 1

    LOG.info(f"Import complete: {counts}")
    return counts
