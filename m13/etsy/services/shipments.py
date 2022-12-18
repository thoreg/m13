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
import os
from io import TextIOWrapper

import requests

from etsy.common import get_auth_token
from etsy.models import Order, Shipment

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv("M13_ETSY_API_KEY")
M13_ETSY_SHOP_ID = os.getenv("M13_ETSY_SHOP_ID")


def do_post(token, order, tracking_code, carrier_name):
    """Do the actual post call to report shipping information."""
    LOG.info(
        f"post shipping infos for o: {order.marketplace_order_id} t: {tracking_code} c: {carrier_name}"
    )

    SHIPMENTS_URL = f"https://openapi.etsy.com/v3/application/shops/{M13_ETSY_SHOP_ID}/receipts/{order.marketplace_order_id}/tracking"

    headers = {"authorization": f"Bearer {token}", "x-api-key": M13_ETSY_API_KEY}
    payload = {"carrier_name": carrier_name, "tracking_code": tracking_code}

    r = requests.post(
        SHIPMENTS_URL,
        headers=headers,
        json=payload,
    )

    LOG.info(f"upload shipping information() r.status_code: {r.status_code}")
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
    if not token:
        LOG.error("No token found")
        return

    f = TextIOWrapper(csv_file.file, encoding="latin1")
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        if not row[0].startswith("ETSY"):
            continue

        LOG.info(row)

        tracking_info = row[3]
        if not tracking_info:
            LOG.error(f"Tracking info not found - row: {row}")
            continue

        order_id = row[0].lstrip("ETSY")
        try:
            order = Order.objects.select_related("delivery_address").get(
                marketplace_order_id=order_id
            )
        except Order.DoesNotExist:
            LOG.error(f"Order not found {order_id} - row {row}")
            continue

        carrier = row[4]
        if carrier.startswith("DHL"):
            carrier = "DHL"
        else:
            carrier = "HERMES"

        status_code, response = do_post(token, order, tracking_info, carrier)

        Shipment.objects.create(
            order=order,
            carrier=carrier,
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response,
        )
