"""Shipment related code lives here.

POST /api/v1/orders/ship

{
  "items": [
    {
      "order_items": [
        1
      ],
      "carrier_key": "DHL_STD_NATIONAL",
      "shipment_tracking_key": "123456789",
      "return_tracking_key": "123456789"
    }
  ]
}

"""

import csv
import json
import logging
import os
import string
import time
from datetime import datetime
from io import TextIOWrapper
from pprint import pprint

import requests

from aboutyou.models import BatchRequest, Order, Shipment
from m13.lib import log as mlog

from .common import API_BASE_URL

LOG = logging.getLogger(__name__)

SHIPMENTS_URL = f"{API_BASE_URL}/api/v1/orders/ship"
BATCH_REQUEST_RESULT_URL = f"{API_BASE_URL}/api/v1/results/ship-orders"


def get_payload(order, tracking_info, return_shipment_code):
    """Return the payload for all orderitems of the given order.
    {
        "items": [{
            "order_items": [
                1
            ],
            "carrier_key": "DHL_STD_NATIONAL",
            "shipment_tracking_key": "123456789",
            "return_tracking_key": "123456789"
        }]
    }
    """
    # LOG.info(order.__dict__)
    # LOG.info(order.delivery_address.__dict__)
    # for oi in order.orderitem_set.all():
    #     LOG.info(oi.__dict__)

    order_items = []
    for oi in order.orderitem_set.all():
        order_items.append(oi.position_item_id)

    return json.dumps(
        {
            "items": [
                {
                    "order_items": order_items,
                    "carrier_key": "DHL_STD_NATIONAL",
                    "shipment_tracking_key": tracking_info,
                    "return_tracking_key": return_shipment_code,
                }
            ]
        }
    )


def do_post(headers, order, tracking_info, return_shipment_code):
    payload = get_payload(order, tracking_info, return_shipment_code)
    LOG.info(f"payload: {payload}")
    r = requests.post(
        SHIPMENTS_URL,
        headers=headers,
        data=payload,
    )

    LOG.info(f"post - status_code: {r.status_code}")
    LOG.info(r.json())

    return r.status_code, r.json()


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    token = os.getenv("M13_ABOUTYOU_TOKEN")
    if not token:
        LOG.error("M13_ABOUTYOU_TOKEN not found")
        return

    headers = {
        "X-API-Key": token,
        "Content-Type": "application/json;charset=UTF-8",
    }

    f = TextIOWrapper(csv_file.file, encoding="latin1")
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        if not row[0].startswith("ayou-"):
            LOG.info(f"Skip non ay row: {row}")
            continue

        tracking_info = row[3]
        if not tracking_info:
            mlog.error(LOG, f"Tracking info not found - row: {row}")
            continue

        marketplace_order_id = row[0]
        try:
            order = Order.objects.select_related("delivery_address").get(
                marketplace_order_id=marketplace_order_id
            )
        except Order.DoesNotExist:
            mlog.error(LOG, f"Order not found {marketplace_order_id} - row {row}")
            continue

        return_shipment_code = row[5]

        status_code, response = do_post(
            headers, order, tracking_info, return_shipment_code
        )
        if status_code != requests.codes.ok:
            LOG.error(f"update shipping information for {marketplace_order_id}) failed")
            LOG.error(response)
            return

        # Check the result - Wait until processing on AY side is done
        batch_request_id = response.json()["batchRequestId"]
        br, _created = BatchRequest.objects.get_or_create(id=batch_request_id)

        for waiting_time_in_seconds in [1, 2, 4, 8, 16, 32]:
            response = requests.get(
                f"{BATCH_REQUEST_RESULT_URL}?batch_request_id={batch_request_id}",
                headers=headers,
                timeout=60,
            )
            status = response.json()["status"]
            br.status = status
            br.save()

            LOG.info(f"batch_request: {br.id} status: {status}")

            if status == "completed":
                break

            LOG.info(f"waiting for {waiting_time_in_seconds} seconds")
            time.sleep(waiting_time_in_seconds)

        Shipment.objects.create(
            order=order,
            carrier="DHL",
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response,
        )
