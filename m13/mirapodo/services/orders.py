"""Import Orders from marketplace Mirapodo"""
import logging
import os
import time
from pprint import pprint

import requests
import xmltodict
from colorama import Fore, Style
from lxml import etree
from requests.exceptions import HTTPError

from mirapodo.models import Address, Order, OrderItem

ORDER_IMPORT_URL = os.environ['M13_MIRAPODO_ORDER_IMPORT_URL']
USER_NAME = os.environ['M13_MIRAPODO_USER_NAME']
HNR = os.environ['M13_MIRAPODO_HNR']
PASSWD = os.environ['M13_MIRAPODO_PASSWORD']

DELIVERY_FEE_STANDARD = 'Hermes HSI'

LOG = logging.getLogger(__name__)


def import_order(order_dict):
    """Create or update a single order."""
    pprint(order_dict)

    address_data = order_dict.get('SHIP_TO')
    order_data = order_dict['ORDER_DATA']
    order_items = order_dict['ITEMS']['ITEM']

    street_no = address_data.get('STREET_NO').split()
    street = ' '.join(street_no[:-1])
    house_number = street_no[-1]
    delivery_address, _created = Address.objects.get_or_create(
        addition=address_data.get('TB_ID'),
        city=address_data.get('CITY'),
        country_code=address_data.get('COUNTRY'),
        first_name=address_data.get('FIRSTNAME'),
        house_number=house_number,
        last_name=address_data.get('LASTNAME'),
        street=street,
        title=address_data.get('TITLE'),
        zip_code=address_data.get('ZIP'),
    )

    marketplace_order_id = order_data.get('TB_ID')
    order, created = Order.objects.get_or_create(
        marketplace_order_id=marketplace_order_id,
        defaults={
            'delivery_address': delivery_address,
            'delivery_fee': DELIVERY_FEE_STANDARD,
            'invoice_address': delivery_address,
            'order_date': order_data.get('DATE_CREATED')
        }
    )
    if created:
        print(Fore.GREEN + f'Order {marketplace_order_id} imported')
        print(Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f'Order {marketplace_order_id} already known')
        print(Style.RESET_ALL)

    if len(order_dict['ITEMS'].keys()) != 1:
        LOG.error('[ mirapodo ] - other keys then items found - check this')
        LOG.error(order_dict['ITEMS'])

    def _get_or_create_orderitem(oi):
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            position_item_id=oi.get('TB_ID'),
            defaults={
                'billing_text': oi.get('BILLING_TEXT')[:32],
                'channel_id': oi.get('CHANNEL_ID'),
                'channeld_sku': oi.get('CHANNEL_SKU'),
                'date_created': oi.get('DATE_CREATED'),
                'ean': oi.get('EAN'),
                'item_price': oi.get('ITEM_PRICE'),
                'quantity': oi.get('QUANTITY'),
                'sku': oi.get('SKU'),
                'transfer_price': oi.get('TRANSFER_PRICE'),
            }
        )
        return order_item, created

    if isinstance(order_items, list):
        for oi in order_items:
            _get_or_create_orderitem(oi)
    else:
        _get_or_create_orderitem(order_items)


def import_orders(xml_string):
    """Walk through all orders within a given xml string and trigger import."""
    parsed = xmltodict.parse(xml_string)

    if isinstance(parsed['ORDER_LIST']['ORDER'], list):
        for order_xml in parsed['ORDER_LIST']['ORDER']:
            import_order(order_xml)
    else:
        import_order(parsed['ORDER_LIST']['ORDER'])


def fetch_orders():
    """..."""

    print(f'ORDER_IMPORT_URL: {ORDER_IMPORT_URL}')
    print(f'USER_NAME: {USER_NAME}')
    print(f'PASSWD: {PASSWD}')
    print(f'HNR: {HNR}')

    for tb_id in range(0, 500):
        print(f'Fetching order no: {tb_id}')
        try:
            response = requests.get(
                f'{ORDER_IMPORT_URL}/{tb_id}',
                auth=(USER_NAME, PASSWD)
            )
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            import_orders(response.content)

        time.sleep(1)
