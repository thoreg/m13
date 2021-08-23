"""Shipment related code lives here.

POST /v1/shipments gets the following payload

{
    "trackingKey": {
        "carrier": "HERMES",
        "trackingNumber": "H1234567890123456789"
    },
    "shipDate": "2019-10-11T07:49:12.642Z",
    "shipFromAddress": {
        "city": "Dresden",
        "countryCode": "DEU",
        "zipCode": "01067"
    },
    "positionItems": [
        {
            "positionItemId": "b01b8ad2-a49c-47fc-8ade-8629ec000020",
            "salesOrderId": "bf43d748-f13d-49ca-b2e2-1824e9000021",
            "returnTrackingKey": {
                "carrier": "DHL",
                "trackingNumber": "577546565072"
            }
        },
        {
            "positionItemId": "b01b8ad2-a49c-47fc-8ade-8629ec000022",
            "salesOrderId": "bf43d748-f13d-49ca-b2e2-1824e9000021",
            "returnTrackingKey": {
                "carrier": "DHL",
                "trackingNumber": "577546565072"
            }
        }
    ]
}

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

CARRIER_MAP = {
    'Hermes XS': 'HERMES',
    'Hermes S': 'HERMES',
}
SHIPMENTS_URL = 'https://api.otto.market/v1/shipments'


def get_payload(order_id, tracking_info, carrier):
    """Return the payload for all orderitems of the given order."""
    order = (
        Order.objects.select_related('delivery_address')
                     .get(marketplace_order_id=order_id))

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
            'salesOrderId': order_id,
            'returnTrackingKey': {
                'carrier': carrier,
                'trackingNumber': tracking_info
            }
        })

    data['positionItems'] = order_items
    LOG.info(f'Return data: {data}')
    return data


def do_post(token, order_id, tracking_info, carrier):
    payload = get_payload(order_id, tracking_info, carrier)

    LOG.info(f'upload for o: {order_id} t: {tracking_info} c: {carrier}')
    print(f'upload for o: {order_id} t: {tracking_info} c: {carrier}')

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
    print(f'upload shipping information() r.status_code: {r.status_code}')
    response = r.json()
    LOG.info(response)
    print(response)

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
        if not row[18].startswith('OTTO'):
            continue

        tracking_info = row[17]
        if not tracking_info:
            LOG.error(f'Tracking info not found - row: {row}')
            continue

        order_id = row[18].replace('OTTO ', '')
        order = Order.objects.get(marketplace_order_id=order_id)
        if not order:
            LOG.error(f'Order not found {order_id} - row {row}')
            continue

        carrier = row[19]
        if carrier.startswith('Hermes'):
            carrier = 'HERMES'
        else:
            carrier = 'DHL'

        LOG.info(f'o: {order_id} t: {tracking_info} c: {carrier}')

        status_code, response = do_post(token, order_id, tracking_info, carrier)

        Shipment.objects.create(
            order=order,
            carrier=carrier,
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response
        )
