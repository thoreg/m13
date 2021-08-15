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
import json
import logging
import os
import sys
from functools import reduce
from pprint import pformat

import requests
from colorama import Fore
from django.core.management.base import BaseCommand, CommandError
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth

from otto.models import Address, Order, OrderItem

LOG = logging.getLogger(__name__)

TOKEN_URL = "https://api.otto.market/v1/token"
ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

ORDER_STATUS_LIST = [
    'ANNOUNCED',
    'CANCELLED_BY_MARKETPLACE',
    'CANCELLED_BY_PARTNER',
    'PROCESSABLE',
    'RETURNED',
    'SENT',
]

token = ""

if not all([USERNAME, PASSWORD]):
    print("\nyou need to define username and password\n")
    sys.exit(1)


def safenget(dct, key, default=None):
    """Get nested dict items safely."""
    try:
        return reduce(dict.__getitem__, key.split('.'), dct)
    # KeyError is for key not available, TypeError is for nested item not
    # subscriptable, e.g. getting a.b.c, but a.b is None or an int.
    except (KeyError, TypeError):
        return default


def get_auth_token():
    """Get authentication token for further communication."""
    LOG.info('Get auth token')
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "cache-control": "no-cache",
    }
    data = {
        "username": USERNAME,
        "grant_type": "password",
        "client_id": "token-otto-api",
        "password": PASSWORD,
    }
    r = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
    )
    return r.json().get("access_token")


def fetch_orders(token, status, from_order_date):
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
    }
    r = requests.get(
        ORDERS_URL,
        headers=headers,
    )
    LOG.info(f"get_orders() response_status_code: {r.status_code}")
    return r.json()


def get_orders(status, from_order_date):
    """Fetch all orders with given status newer than the specified date."""
    if not status:
        LOG.error('No status')
        return

    if not from_order_date:
        LOG.error('No from order date')
        return

    LOG.info(f'Get orders with status {status} newer then {from_order_date}')

    response = fetch_orders(token, status, from_order_date)
    announced_orders = {}

    for entry in response.get("resources", []):
        marketplace_order_id = entry.get('salesOrderId')
        delivery_address = entry.get('deliveryAddress')

        # Orders with internal order status ANNOUNCED do not have a delivery
        # address set yet - just track these in a dict
        if not delivery_address:
            self.stdout.write(self.style.WARNING(
                f'Order {marketplace_order_id} has no delivery address'
            ))
            for item in entry.get('positionItems'):
                sku = item['product'].get('sku')
                fulfillment_status = item.get('fulfillmentStatus')
                self.stdout.write(self.style.WARNING(
                    f'   {sku} fulfillmentStatus {fulfillment_status}'
                ))

                if sku not in announced_orders:
                    announced_orders[sku] = {
                        'title': item['product'].get('productTitle'),
                        'sku': sku,
                        'number': 1
                    }
                else:
                    announced_orders[sku]['number'] += 1

            continue

        delivery_address, _created = Address.objects.get_or_create(
            addition=entry.get('deliveryAddress').get('addition'),
            city=entry.get('deliveryAddress').get('city'),
            country_code=entry.get('deliveryAddress').get('countryCode'),
            first_name=entry.get('deliveryAddress').get('firstName'),
            house_number=entry.get('deliveryAddress').get('houseNumber'),
            last_name=entry.get('deliveryAddress').get('lastName'),
            street=entry.get('deliveryAddress').get('street'),
            title=entry.get('deliveryAddress').get('title'),
            zip_code=entry.get('deliveryAddress').get('zipCode'),
        )
        invoice_address, _created = Address.objects.get_or_create(
            addition=entry.get('deliveryAddress').get('addition'),
            city=entry.get('deliveryAddress').get('city'),
            country_code=entry.get('deliveryAddress').get('countryCode'),
            first_name=entry.get('deliveryAddress').get('firstName'),
            house_number=entry.get('deliveryAddress').get('houseNumber'),
            last_name=entry.get('deliveryAddress').get('lastName'),
            street=entry.get('deliveryAddress').get('street'),
            title=entry.get('deliveryAddress').get('title'),
            zip_code=entry.get('deliveryAddress').get('zipCode'),
        )

        order, created = Order.objects.get_or_create(
            marketplace_order_id=marketplace_order_id,
            defaults={
                'delivery_address': delivery_address,
                'delivery_fee': entry.get('initialDeliveryFees'),
                'invoice_address': invoice_address,
                'last_modified_date': entry.get('lastModifiedDate'),
                'marketplace_order_number': entry.get('orderNumber'),
                'order_date': entry.get('orderDate'),
            }
        )
        if created:
            print(Fore.GREEN + f'Order {marketplace_order_id} imported')
        else:
            print(Fore.YELLOW + f'Order {marketplace_order_id} already known')

        for oi in entry.get('positionItems'):
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                position_item_id=oi.get('positionItemId'),
                defaults={
                    'cancellation_date': oi.get('cancellationDate'),
                    'expected_delivery_date': oi.get('expectedDeliveryDate'),
                    'fulfillment_status': oi.get('fulfillmentStatus'),
                    'price_in_cent':
                        oi.get('itemValueGrossPrice').get('amount') * 100,
                    'currency': oi.get('itemValueGrossPrice').get('currency'),
                    'article_number': oi.get('product').get('articleNumber'),
                    'ean': oi.get('product').get('ean'),
                    'product_title': oi.get('product').get('productTitle'),
                    'sku': oi.get('product').get('sku'),
                    'vat_rate': int(oi.get('product').get('vatRate')),
                    'returned_date': oi.get('returnedDate'),
                    'sent_date': oi.get('sentDate'),
                    'carrier': safenget(oi, 'trackingInfo.carrier'),
                    'carrier_service_code': safenget(oi, 'trackingInfo.carrierServiceCode'),
                    'tracking_number': safenget(oi, 'trackingInfo.trackingNumber'),
                }
            )
            if not created:
                order_item.fulfillment_status = oi.get('fulfillmentStatus')
                order_item.save()
