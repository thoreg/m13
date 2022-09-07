
import datetime
from decimal import Decimal

import pytest
from freezegun import freeze_time

from mirapodo.models import Address, Order, OrderItem
from mirapodo.services.orders import import_orders


def verify_addresses(addresses):
    """Things look like expected."""
    assert [a for a in addresses] == [
        {
            'id': 1,
            'created': datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'modified': datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'addition': '395',
            'city': 'Schwarmstedt',
            'country_code': 'DE',
            'first_name': 'M.',
            'house_number': '21',
            'last_name': 'F.',
            'street': "['A.', 'A.']",
            'title': 'Frau',
            'zip_code': '29690'
        }, {
            'id': 2,
            'created': datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'modified': datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'addition': '397',
            'city': 'Jena',
            'country_code': 'DE',
            'first_name': 'P.',
            'house_number': '8',
            'last_name': 'S.',
            'street': "['C.', 'B.', 'S.']",
            'title': 'Herr',
            'zip_code': '07749'
        }]


def verify_orders(orders):
    """We have two orders in the system."""
    assert [o for o in orders] == [{
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'delivery_address_id': 1,
        'delivery_fee': 'Hermes HSI',
        'id': 1,
        'internal_status': 'IMPORTED',
        'invoice_address_id': 1,
        'marketplace_order_id': '409',
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_date': datetime.datetime(2022, 9, 2, 7, 16, 1, tzinfo=datetime.timezone.utc)
    }, {'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'delivery_address_id': 2,
        'delivery_fee': 'Hermes HSI',
        'id': 2,
        'internal_status': 'IMPORTED',
        'invoice_address_id': 2,
        'marketplace_order_id': '411',
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_date': datetime.datetime(2022, 9, 4, 19, 45, 43, tzinfo=datetime.timezone.utc)}]


def verify_order_items(order_items):
    """We have two orders in the system."""
    assert [oi for oi in order_items] == [{
        'billing_text': 'Women Bomberjacke - Übergangsjac',
        'channel_id': '1',
        'channeld_sku': '20919197',
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'date_created': datetime.datetime(2022, 9, 2, 7, 16, 1, tzinfo=datetime.timezone.utc),
        'ean': '0781491969945',
        'id': 1,
        'item_price': Decimal('64.95'),
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 1,
        'position_item_id': '527',
        'quantity': 1,
        'sku': 'women-bom-bo-l',
        'transfer_price': Decimal('54.58')
    }, {
        'billing_text': 'Women Bomberjacke - Übergangsjac',
        'channel_id': '2',
        'channeld_sku': '20919200',
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'date_created': datetime.datetime(2022, 9, 2, 7, 16, 1, tzinfo=datetime.timezone.utc),
        'ean': '0781491969952',
        'id': 2,
        'item_price': Decimal('64.95'),
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 1,
        'position_item_id': '529',
        'quantity': 1,
        'sku': 'women-bom-bo-xl',
        'transfer_price': Decimal('54.58')
    }, {
        'billing_text': 'Wasserabweisender Roll-Top Rucks',
        'channel_id': '1',
        'channeld_sku': '20919043',
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'date_created': datetime.datetime(2022, 9, 4, 19, 45, 43, tzinfo=datetime.timezone.utc),
        'ean': '0781491968887',
        'id': 3,
        'item_price': Decimal('104.95'),
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 2,
        'position_item_id': '531',
        'quantity': 1,
        'sku': 'ROLLTOP-MU',
        'transfer_price': Decimal('88.19')}]


@freeze_time('2022-09-07')
@pytest.mark.django_db
def test_import_orders():
    """XML from order file gets imported properly."""
    with open('mirapodo/tests/data/response_with_multiple_orders.xml', 'r') as f:
        xml_string = f.read()

    # basic import
    import_orders(xml_string)

    verify_addresses(Address.objects.all().values())
    verify_orders(Order.objects.all().values())
    verify_order_items(OrderItem.objects.all().values())

    # multiple import does not mess up things
    import_orders(xml_string)
    import_orders(xml_string)

    verify_addresses(Address.objects.all().values())
    verify_orders(Order.objects.all().values())
    verify_order_items(OrderItem.objects.all().values())
