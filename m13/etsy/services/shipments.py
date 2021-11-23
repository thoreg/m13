"""Shipment related code lives here.

POST /v3/application/shops/{shop_id}/receipts/{receipt_id}/tracking

Submits tracking information for a Shop Receipt, which creates a Shop Receipt
Shipment entry for the given receipt_id. Each time you successfully submit
tracking info, Etsy sends a notification email to the buyer User.

When send_bcc is true, Etsy sends shipping notifications to the seller as well.
When tracking_code and carrier_name aren't sent, the receipt is marked as
shipped only.

AUTHORIZATIONS:
    api_keyoauth2 (transactions_wemail_r)

PATH PARAMETERS
    shop_id -> required integer >= 1
        The unique positive non-zero numeric ID for an Etsy Shop.
    receipt_id -> required integer >= 1
        The receipt to submit tracking for.

REQUEST BODY SCHEMA: application/x-www-form-urlencoded
    tracking_code -> string
        The tracking code for this receipt.
    carrier_name -> string
        The carrier name for this receipt.
    send_bcc -> boolean
        If true, the shipping notification will be sent to the seller as wel

"""
import csv
import logging
from datetime import datetime
from io import TextIOWrapper
from pprint import pprint

import requests

from otto.common import get_auth_token
from otto.models import Order, Shipment

LOG = logging.getLogger(__name__)

SHIPMENTS_URL = 'https://openapi.etsy.com/v3/application/shops/{shop_id}/receipts/{receipt_id}/tracking'


def get_payload(order, tracking_info, carrier):
    """Return the payload for all orderitems of the given order."""
    LOG.info(order.__dict__)
    LOG.info(order.delivery_address.__dict__)
    for oi in order.orderitem_set.all():
        LOG.info(oi.__dict__)

    data = {
        'trackingKey': {
            'carrier': carrier,
            'trackingNumber': tracking_info
        },
        'shipDate': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'shipFromAddress': {
            'city': order.delivery_address.city,
            'countryCode': order.delivery_address.country_code,
            'zipCode': order.delivery_address.zip_code
        },
    }
    order_items = []
    for oi in order.orderitem_set.all():
        order_items.append({
            'positionItemId': oi.position_item_id,
            'salesOrderId': order.marketplace_order_id,
            'returnTrackingKey': {
                'carrier': carrier,
                'trackingNumber': tracking_info
            }
        })

    data['positionItems'] = order_items
    LOG.info(f'Return data: {data}')
    return data


def do_post(token, order, tracking_info, carrier):
    payload = get_payload(order, tracking_info, carrier)

    LOG.info(
        f'upload for o: {order.marketplace_order_number} t: {tracking_info} c: {carrier}')

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
    }

    pprint(payload)

    r = requests.post(
        SHIPMENTS_URL,
        headers=headers,
        json=payload,
    )

    LOG.info(f'upload shipping information() r.status_code: {r.status_code}')
    LOG.info(r.json())

    return r.status_code, r.json()


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    token = get_auth_token()
    f = TextIOWrapper(csv_file.file, encoding='latin1')
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        if not row[0].startswith('b'):
            continue

        tracking_info = row[3]
        if not tracking_info:
            LOG.error(f'Tracking info not found - row: {row}')
            continue

        order_number = row[0]
        try:
            order = (
                Order.objects.select_related('delivery_address')
                     .get(marketplace_order_number=order_number))
        except Order.DoesNotExist:
            LOG.error(f'Order not found {order_number} - row {row}')
            continue

        carrier = row[4]
        if carrier.startswith('DHL'):
            carrier = 'DHL'
        else:
            carrier = 'HERMES'

        LOG.info(f'o: {order_number} t: {tracking_info} c: {carrier}')

        status_code, response = do_post(token, order, tracking_info, carrier)

        Shipment.objects.create(
            order=order,
            carrier=carrier,
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response
        )
