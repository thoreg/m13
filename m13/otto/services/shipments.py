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
import requests
from pprint import pprint
import logging
from io import TextIOWrapper
from otto.common import get_auth_token

CARRIER = 'HERMES'

LOG = logging.getLogger(__name__)


def get_payload(marketplace_order_id, carrier, tracking_number):
    data = {
        'trackingKey': {
            'carrier': carrier,
            'trackingNumber': tracking_number
        },
        'shipDate': "2019-10-11T07:49:12.642Z",
        'shipFromAddress': {
            'city': 'Dresden',
            'countryCode': 'DEU',
            'zipCode': '01067'
        },
        'positionItems': [
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
    return data


def do_post(token, marketplace_order_id, tracking_number):
    SHIPMENTS_URL = 'https://api.otto.market/v1/shipments'
    payload = get_payload(marketplace_order_id, CARRIER, tracking_number)

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
    print(f"upload shipping information() r.status_code: {r.status_code}")
    response = r.json()


def handle_uploaded_file(csv_file):
    """Handle uploaded csv file and do the POST.

    Get the two important fields from the line and create payload out of it
    and do upload the information.

    request.FILES gives you binary files, but the csv module wants to have
    text-mode files instead.
    """
    token = get_auth_token()
    # UnicodeDecodeError
    # f = TextIOWrapper(csv_file.file, encoding='utf-8')
    f = TextIOWrapper(csv_file.file, encoding='latin1')
    reader = csv.reader(f, delimiter=';')
    for row in reader:
      LOG.info(row)
      # carrier?
      do_post(token, row[18], row[17])
