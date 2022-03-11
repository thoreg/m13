"""Upload stock information to OTTO."""
import os
import requests
import json

import logging

from otto.common import get_auth_token
from otto.services.orders import fetch_next_slice, fetch_orders_by_status, save_orders
from datetime import datetime

LOG = logging.getLogger(__name__)

M13_OTTO_FEED_URL = os.getenv('M13_OTTO_FEED_URL')

OTTO_QUANTITIES_URL = 'https://api.otto.market/v2/quantities'


def sync_stock():
    """Get the feed and upload stock information."""
    token = get_auth_token()
    LOG.info(f'token: {token}')
    headers = {
        'Authorization': f'Bearer {token}',
    }

    feed = requests.get(M13_OTTO_FEED_URL)
    stock = json.loads(feed.content)

    payload = []

    LOG.info('\n\nBEFORE:')
    for product in stock:
        # LOG.info(product)
        sku = product['sku']
        quantity = product['quantity']

        if sku in ['alic-rolltop-az', 'alic-rolltop-bb']:

            r = requests.get(f'{OTTO_QUANTITIES_URL}/{sku}', headers=headers)
            LOG.info(r.json())

            payload.append({
                "lastModified": f"{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z",
                "quantity": quantity,
                "sku": sku
            })

    LOG.info('\n\nUPDATE CALL:')
    LOG.info(f'payload: {payload}')
    resp = requests.post(f'{OTTO_QUANTITIES_URL}', headers=headers, json=payload)
    if resp.status_code != requests.codes.ok:
        LOG.error('Error occurred in OTTO stock sync')
        LOG.error(resp.__dict__)

    LOG.info('\n\nAFTER:')
    for product in stock:
        # LOG.info(product)
        sku = product['sku']
        quantity = product['quantity']

        if sku in ['alic-rolltop-az', 'alic-rolltop-bb']:

            r = requests.get(f'{OTTO_QUANTITIES_URL}/{sku}', headers=headers)
            LOG.info(r.json())
