"""Shipment related code lives here.

POST request to http(s)://rest.trade-server.net/HNR/messages/?

with the following payload

<?xml version="1.0" encoding="utf-8"?>
<MESSAGES_LIST>
    <MESSAGE>
        <MESSAGE_TYPE>SHIP</MESSAGE_TYPE>                           - Nachrichtentyp -
        <TB_ORDER_ID>3</TB_ORDER_ID>                                - Eindeutige Auftragsnummer -
        <TB_ORDER_ITEM_ID>1</TB_ORDER_ITEM_ID>                      - Eindeutige Positionsnummer -
        <SKU>4711</SKU>                                             - SKU der Position -
        <QUANTITY>1</QUANTITY>                                      - Liefermenge -
        <CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE> - Versandart -
        <IDCODE>123456789</IDCODE>                                  - Shipcode -
        <IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL>          - BOGUS BILLO VALUE
    </MESSAGE>
</MESSAGES_LIST>

Response:

<?xml version="1.0" encoding="UTF-8"?>
<tradebyte>
    <state>message created successfully</state>
</tradebyte>

"""
import csv
import logging
import os
from io import TextIOWrapper

import requests
from requests.models import codes

from m13.lib import log as mlog
from mirapodo.models import Order, Shipment

LOG = logging.getLogger(__name__)

USER_NAME = os.environ["M13_MIRAPODO_USER_NAME"]
HNR = os.environ["M13_MIRAPODO_HNR"]
PASSWD = os.environ["M13_MIRAPODO_PASSWORD"]
SHIPMENTS_URL = f"https://rest.trade-server.net/{HNR}/messages/?"
CARRIER = "DHL_STD_NATIONAL"


class ApiCallFailed(Exception):
    pass


def _strip_payload(payload):
    """Remove newline and whitespace to get something mirapodo understands."""
    payload = payload.strip()
    payload = payload.replace("\n", "")
    payload = " ".join(payload.split())
    payload = payload.replace("> <", "><")
    return payload


def _get_playload_start():
    return '<?xml version="1.0" encoding="utf-8"?><MESSAGES_LIST>'


def _get_playload_end():
    return "</MESSAGES_LIST>"


def get_payload(orderitem, tracking_info):
    """Return the payload for all orderitems of the given order."""
    order_id = orderitem.order.marketplace_order_id.lstrip("TB_")
    return f"""
        <MESSAGE>
            <MESSAGE_TYPE>SHIP</MESSAGE_TYPE>
            <TB_ORDER_ID>{order_id}</TB_ORDER_ID>
            <TB_ORDER_ITEM_ID>{orderitem.position_item_id}</TB_ORDER_ITEM_ID>
            <SKU>{orderitem.sku}</SKU>
            <QUANTITY>{orderitem.quantity}</QUANTITY>
            <CARRIER_PARCEL_TYPE>{CARRIER}</CARRIER_PARCEL_TYPE>
            <IDCODE>{tracking_info}</IDCODE>
            <IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL>
        </MESSAGE>
    """


def _post(url, auth, data, headers):
    """Do the actual call to the external API."""
    return requests.post(url, auth=auth, data=data, headers=headers)


def upload_tracking_info(order, tracking_info):
    """Update tracking info per orderitem.

    Submit xml data to the POST endpoint.
    """
    headers = {"Content-Type": "application/xml"}

    payload = _get_playload_start()

    for orderitem in order.orderitem_set.all():
        payload += get_payload(orderitem, tracking_info)

    payload += _get_playload_end()
    payload = _strip_payload(payload)

    print(f"SHIPMENTS_URL: {SHIPMENTS_URL}")
    print(f"PAYLOAD: {payload}")

    response = _post(
        f"{SHIPMENTS_URL}", auth=(USER_NAME, PASSWD), data=payload, headers=headers
    )

    msg = f"resp: {response.status_code} : {response.text}"
    if response.status_code == codes.created:
        LOG.info(msg)
        LOG.info("mark all orderitems as shipped")
        for orderitem in order.orderitem_set.all():
            orderitem.mark_as_shipped()
    else:
        mlog.error(LOG, msg)
        raise ApiCallFailed("API call to mirapodo failed")

    return 200, "SUCCESS"


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    f = TextIOWrapper(csv_file.file, encoding="latin1")
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        # Check if row is considered to be an 'Mirapodo ROW'
        if not row[0].startswith("TB_"):
            LOG.info("Not a mirapodo row")
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

        LOG.info(f"o: {marketplace_order_id} t: {tracking_info}")

        try:
            status_code, response = upload_tracking_info(order, tracking_info)
        except ApiCallFailed:
            status_code = 409
            response = "API call failed - please check logs"

        Shipment.objects.create(
            order=order,
            carrier=CARRIER,
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response,
        )
        order.internal_status = Order.Status.SHIPPED
        order.save()
