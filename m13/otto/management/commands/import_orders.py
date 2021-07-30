import json
import os
import pprint
import sys
from functools import reduce
from pprint import pformat

import requests
from django.core.management.base import BaseCommand, CommandError
from fastapi import FastAPI
from requests.auth import HTTPBasicAuth

from otto.models import Address, Order, OrderItem

TOKEN_URL = "https://api.otto.market/v1/token"
ORDERS_URL = "https://api.otto.market/v4/orders"

USERNAME = os.getenv("OTTO_API_USERNAME")
PASSWORD = os.getenv("OTTO_API_PASSWORD")

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


class Command(BaseCommand):
    help = "Import Orders from OTTO"

    def handle(self, *args, **options):

        print(f"Get the token ...")
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
        response = r.json()
        token = response.get("access_token")

        print(f"Get the orders ...")
        headers = {
            "Authorization": f"Bearer {token}",
        }
        r = requests.get(
            ORDERS_URL,
            headers=headers,
        )
        print(f"get_orders() response_status_code: {r.status_code}")
        response = r.json()

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
                self.stdout.write(self.style.SUCCESS(
                    f'Order {marketplace_order_id} imported'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Order {marketplace_order_id} already known'
                ))
            for oi in entry.get('positionItems'):
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    position_item_id=oi.get('positionItemId'),
                    defaults={
                        'cancellation_date': oi.get('cancellationDate'),
                        'expected_delivery_date': oi.get('expectedDeliveryDate'),
                        'fulfillment_status': oi.get('fulfillmentStatus'),
                        'price_in_cent': int(
                            oi.get('itemValueGrossPrice').get('amount')) * 100,
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

        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(announced_orders)
