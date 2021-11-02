import logging
import os

import requests
from colorama import Fore

from m13.common import timestamp_from_epoch

from .models import Address, Order, OrderItem

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv('M13_ETSY_API_KEY')
M13_ETSY_SHOP_ID = os.getenv('M13_ETSY_SHOP_ID')

STATUS_MAP = {
    'Completed': Order.Status.COMPLETED,
    'Open': Order.Status.OPEN,
    'Paid': Order.Status.PAID,
    'Payment Processing': Order.Status.PAYMENT_PROCESSING
}


def get_receipts(token):
    """Return receipts as json."""
    headers = {
        'x-api-key': M13_ETSY_API_KEY,
        'authorization': f'Bearer {token}'
    }
    url = f'https://openapi.etsy.com/v3/application/shops/{M13_ETSY_SHOP_ID}/receipts'
    r = requests.get(url, headers=headers)
    LOG.info(r.__dict__)
    LOG.info(r.status_code)
    return r.json()


def process_receipts(data):
    """Process list of shop receipts.

    https://developers.etsy.com/documentation/reference/#operation/getShopReceipts
    """
    if 'results' not in data:
        LOG.error('No results in data')
        return

    for d in data['results']:
        process_receipt(d)


def process_receipt(data):
    """Process single receipt/order."""
    delivery_address, _created = Address.objects.get_or_create(
        buyer_email=data.get('buyer_email'),
        buyer_user_id=data.get('buyer_user_id'),
        city=data.get('city'),
        country_code=data.get('country_iso'),
        formatted_address=data.get('formatted_address'),
        zip_code=data.get('zip'),
    )

    marketplace_order_id = data.get('receipt_id')
    order, created = Order.objects.get_or_create(
        marketplace_order_id=marketplace_order_id,
        defaults={
            'delivery_address': delivery_address,
            'delivery_fee': data.get('total_shipping_cost'),
            'last_modified_date': timestamp_from_epoch(
                data.get('update_timestamp')),
            'order_date': timestamp_from_epoch(data.get('create_timestamp')),
            'status': STATUS_MAP[data.get('status')]
        }
    )
    if created:
        print(Fore.GREEN + f'Order {marketplace_order_id} imported')
    else:
        print(Fore.YELLOW + f'Order {marketplace_order_id} already known')

    carrier = None
    tracking_number = None
    if data['shipments']:
        shipment = data['shipments'][0]
        carrier = shipment['carrier_name']
        tracking_number = shipment['tracking_code']

    for oi in data['transactions']:
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            position_item_id=oi.get('transaction_id'),
            defaults={
                'expected_delivery_date': timestamp_from_epoch(
                    oi.get('expected_ship_date')),
                'fulfillment_status': order.status,
                'price_in_cent': oi.get('price').get('amount'),
                'currency': oi.get('price').get('currency_code'),
                'ean': oi.get('listing_id'),
                'product_title': oi.get('title'),
                'sku': oi.get('sku'),
                'carrier': carrier,
                'tracking_number': tracking_number
            }
        )
        if not created:
            order_item.fulfillment_status = order.status
            order_item.save()