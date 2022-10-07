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
        <IDCODE_RETURN_PROPOSAL></IDCODE_RETURN_PROPOSAL>
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

from mirapodo.models import Order, Shipment

LOG = logging.getLogger(__name__)

USER_NAME = os.environ['M13_MIRAPODO_USER_NAME']
HNR = os.environ['M13_MIRAPODO_HNR']
PASSWD = os.environ['M13_MIRAPODO_PASSWORD']
SHIPMENTS_URL = f"https://rest.trade-server.net/{HNR}/messages/?"
CARRIER = "HERMES"


def get_payload(order, tracking_info):
    """Return the payload for all orderitems of the given order."""
    order_id = order.marketplace_order_id.lstrip("TB_")
    quantity = 0

    for oi in order.orderitem_set.all():
        LOG.info(oi.__dict__)
        quantity += 1
        sku = oi.sku
        orderitem_id = oi.position_item_id

    # TODO: handling of more than one orderitem

    payload = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <MESSAGES_LIST>
            <MESSAGE>
                <MESSAGE_TYPE>SHIP</MESSAGE_TYPE>
                <TB_ORDER_ID>{order_id}</TB_ORDER_ID>
                <TB_ORDER_ITEM_ID>{orderitem_id}</TB_ORDER_ITEM_ID>
                <SKU>{sku}</SKU>
                <QUANTITY>{quantity}</QUANTITY>
                <CARRIER_PARCEL_TYPE>{CARRIER}</CARRIER_PARCEL_TYPE>
                <IDCODE>{tracking_info}</IDCODE>
                <IDCODE_RETURN_PROPOSAL></IDCODE_RETURN_PROPOSAL>
            </MESSAGE>
        </MESSAGES_LIST>
    """
    payload = payload.strip()
    payload = payload.replace('\n', '')
    payload = ' '.join(payload.split())
    payload = payload.replace('> <', '><')

    LOG.info(f'Return payload: {payload}')
    return payload


def _post(url, auth, data, headers):
    """Do the actual call to the external API."""
    return requests.post(url, auth=auth, data=data, headers=headers)


def do_post(order, tracking_info):
    """Submit xml data to the POST endpoint."""
    headers = {'Content-Type': 'application/xml'}
    payload = get_payload(order, tracking_info)

    print(f"SHIPMENTS_URL: {SHIPMENTS_URL}")
    print(f"type payload: {type(payload)}")

    response = _post(
        f'{SHIPMENTS_URL}',
        auth=(USER_NAME, PASSWD),
        data=payload,
        headers=headers
    )

    msg = f"resp: {response.status_code} : {response.text}"
    if response.status_code == codes.ok:
        LOG.info(msg)
        order.internal_status = Order.Status.SHIPPED
        order.save()
    else:
        LOG.error(msg)

    return (response.status_code, response.text)


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    f = TextIOWrapper(csv_file.file, encoding='latin1')
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        # Check if row is considered to be an 'Mirapodo ROW'
        if not row[0].startswith("TB_"):
            LOG.info('Not a mirapodo row')
            continue

        tracking_info = row[3]
        if not tracking_info:
            LOG.error(f'Tracking info not found - row: {row}')
            continue

        marketplace_order_id = row[0].lstrip("TB_")
        try:
            order = (
                Order.objects.select_related('delivery_address')
                     .get(marketplace_order_id=marketplace_order_id))
        except Order.DoesNotExist:
            LOG.error(f'Order not found {marketplace_order_id} - row {row}')
            continue

        LOG.info(f'o: {marketplace_order_id} t: {tracking_info}')

        status_code, response = do_post(order, tracking_info)

        Shipment.objects.create(
            order=order,
            carrier=CARRIER,
            tracking_info=tracking_info,
            response_status_code=status_code,
            response=response
        )
