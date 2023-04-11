"""

https://api.otto.market/docs/05_Orders/v4/order-interface.html

A position item can be in different fulfillment states (attribute 'fulfillmentStatus'):

ANNOUNCED -> A position item which was ordered via payment method Prepayment.
             Such an item can be reserved for the customer in logistics but must
             not be shipped yet.
PROCESSABLE -> This position item is ready to be processed.
SENT -> The item was shipped. These items were processed by the Shipments
        interface.
RETURNED -> The item was returned. These items were processed by the Returns
            interface.
CANCELLED_BY_PARTNER -> This position item was cancelled and won't be processed
                        any further.
CANCELLED_BY_MARKETPLACE -> This position item was cancelled by the market place
                            and won't be processed any further.

"""
import logging
import os
import sys
import urllib.parse
from datetime import datetime, timedelta
from functools import reduce

import requests
from colorama import Fore

from otto.models import Address, Order, OrderItem

LOG = logging.getLogger(__name__)

ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

ORDER_STATUS_LIST = [
    "ANNOUNCED",
    "CANCELLED_BY_MARKETPLACE",
    "CANCELLED_BY_PARTNER",
    "PROCESSABLE",
    "RETURNED",
    "SENT",
]


if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


class InvalidStatus(Exception):
    pass


def safenget(dct, key, default=None):
    """Get nested dict items safely."""
    try:
        return reduce(dict.__getitem__, key.split("."), dct)
    # KeyError is for key not available, TypeError is for nested item not
    # subscriptable, e.g. getting a.b.c, but a.b is None or an int.
    except (KeyError, TypeError):
        return default


def fetch_orders_by_status(token, status, from_order_date=None):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    r = requests.get(
        get_url(status, from_order_date),
        headers=headers,
    )
    LOG.info(f"fetch_orders_by_status() response_status_code: {r.status_code}")
    return r.json()


def fetch_next_slice(token, href):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    r = requests.get(
        ORDERS_URL.replace("/v4/orders", href),
        headers=headers,
    )
    LOG.info(f"fetch_next_slice() response_status_code: {r.status_code}")
    return r.json()


def save_orders(orders_as_json):
    """Fetch all orders with given status newer than the specified date."""
    for entry in orders_as_json.get("resources", []):
        LOG.info(f"otto_oi_entry: {entry}")
        marketplace_order_id = entry.get("salesOrderId")
        delivery_address = entry.get("deliveryAddress")

        # Orders with internal order status ANNOUNCED do not have a delivery
        # address set yet - just track these in a dict
        if not delivery_address:
            print(Fore.YELLOW + f"Order {marketplace_order_id} has no delivery address")
            for item in entry.get("positionItems"):
                sku = item["product"].get("sku")
                fulfillment_status = item.get("fulfillmentStatus")
                print(Fore.YELLOW + f"   {sku} fulfillmentStatus {fulfillment_status}")

            continue

        delivery_address, _created = Address.objects.get_or_create(
            addition=entry.get("deliveryAddress").get("addition"),
            city=entry.get("deliveryAddress").get("city"),
            country_code=entry.get("deliveryAddress").get("countryCode"),
            first_name=entry.get("deliveryAddress").get("firstName"),
            house_number=entry.get("deliveryAddress").get("houseNumber"),
            last_name=entry.get("deliveryAddress").get("lastName"),
            street=entry.get("deliveryAddress").get("street"),
            title=entry.get("deliveryAddress").get("title"),
            zip_code=entry.get("deliveryAddress").get("zipCode"),
        )
        invoice_address, _created = Address.objects.get_or_create(
            addition=entry.get("deliveryAddress").get("addition"),
            city=entry.get("deliveryAddress").get("city"),
            country_code=entry.get("deliveryAddress").get("countryCode"),
            first_name=entry.get("deliveryAddress").get("firstName"),
            house_number=entry.get("deliveryAddress").get("houseNumber"),
            last_name=entry.get("deliveryAddress").get("lastName"),
            street=entry.get("deliveryAddress").get("street"),
            title=entry.get("deliveryAddress").get("title"),
            zip_code=entry.get("deliveryAddress").get("zipCode"),
        )

        order, created = Order.objects.get_or_create(
            marketplace_order_id=marketplace_order_id,
            defaults={
                "delivery_address": delivery_address,
                "delivery_fee": entry.get("initialDeliveryFees"),
                "invoice_address": invoice_address,
                "last_modified_date": entry.get("lastModifiedDate"),
                "marketplace_order_number": entry.get("orderNumber"),
                "order_date": entry.get("orderDate"),
            },
        )
        if created:
            print(Fore.GREEN + f"Order {marketplace_order_id} imported")
        else:
            print(Fore.YELLOW + f"Order {marketplace_order_id} already known")

        for oi in entry.get("positionItems"):
            fulfillment_status = oi.get("fulfillmentStatus")
            expected_delivery_date = oi.get("expectedDeliveryDate")

            if not expected_delivery_date:
                if fulfillment_status == "RETURNED":
                    expected_delivery_date = oi.get("returnedDate")
                elif fulfillment_status == "CANCELLED_BY_MARKETPLACE":
                    expected_delivery_date = oi.get("cancellationDate")

                if not expected_delivery_date:
                    LOG.error("otto - STILL empty expected_delivery_date")
                    LOG.error(oi)

            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                position_item_id=oi.get("positionItemId"),
                defaults={
                    "cancellation_date": oi.get("cancellationDate"),
                    "expected_delivery_date": expected_delivery_date,
                    "fulfillment_status": oi.get("fulfillmentStatus"),
                    "price_in_cent": oi.get("itemValueGrossPrice").get("amount") * 100,
                    "currency": oi.get("itemValueGrossPrice").get("currency"),
                    "article_number": oi.get("product").get("articleNumber"),
                    "ean": oi.get("product").get("ean"),
                    "product_title": oi.get("product").get("productTitle"),
                    "sku": oi.get("product").get("sku"),
                    "vat_rate": int(oi.get("product").get("vatRate")),
                    "returned_date": oi.get("returnedDate"),
                    "sent_date": oi.get("sentDate"),
                    "carrier": safenget(oi, "trackingInfo.carrier"),
                    "carrier_service_code": safenget(
                        oi, "trackingInfo.carrierServiceCode"
                    ),
                    "tracking_number": safenget(oi, "trackingInfo.trackingNumber"),
                },
            )
            if not created:
                order_item.fulfillment_status = oi.get("fulfillmentStatus")
                order_item.save()


def get_url(status, datum=None):
    """Return url to fetch all orders by status.

    Orders newer than datum specified (ISO 8601) will be returned when the
    url is called. Default: last 5 days
    """
    if status not in ORDER_STATUS_LIST:
        raise InvalidStatus(
            f"Invalid status {status} - valid status are {ORDER_STATUS_LIST}"
        )

    if datum:
        datum = datetime.strptime(datum, "%Y-%m-%d")
    else:
        now = datetime.now()
        datum = now - timedelta(days=14)

    fod = datum.astimezone().replace(microsecond=0).isoformat()

    return f"{ORDERS_URL}?fulfillmentStatus={status}&fromOrderDate={urllib.parse.quote_plus(fod)}"
