import datetime
from decimal import Decimal

import pytest
import xmltodict
from django.urls import reverse
from freezegun import freeze_time
from freezegun.api import FakeDatetime

from mirapodo.models import Address, Order, OrderItem
from mirapodo.services.orders import import_orders

MIRAPODO_URLS = [
    'mirapodo_index',
    'mirapodo_orderitems_csv'
]


@pytest.mark.parametrize('m_url', MIRAPODO_URLS)
@pytest.mark.django_db
def test_mirapodo_views(client, django_user_model, m_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse(m_url)
    response = client.get(r_url)
    assert response.status_code == 200


def verify_addresses(addresses):
    """Things look like expected."""
    assert [a for a in addresses] == [
        {
            'id': 1,
            'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'addition': '395',
            'city': 'Schwarmstedt',
            'country_code': 'DE',
            'first_name': 'M.',
            'house_number': '21',
            'last_name': 'F.',
            'street': "A. A.",
            'title': 'Frau',
            'zip_code': '29690'
        }, {
            'id': 2,
            'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
            'addition': '397',
            'city': 'Jena',
            'country_code': 'DE',
            'first_name': 'P.',
            'house_number': '8',
            'last_name': 'S.',
            'street': "C. B. S.",
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
        'mail': 'm.f@gmail.com',
        'marketplace_order_id': 'TB_409',
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_date': datetime.datetime(2022, 9, 2, 7, 16, 1, tzinfo=datetime.timezone.utc)
    }, {'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'delivery_address_id': 2,
        'delivery_fee': 'Hermes HSI',
        'id': 2,
        'internal_status': 'IMPORTED',
        'invoice_address_id': 2,
        'mail': 'ps@web.de',
        'marketplace_order_id': 'TB_411',
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
        'internal_status': 'IMPORTED',
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
        'internal_status': 'IMPORTED',
        'item_price': Decimal('64.95'),
        'modified': FakeDatetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 1,
        'position_item_id': '529',
        'quantity': 1,
        'sku': 'women-bom-bo-xl',
        'transfer_price': Decimal('54.58')
    }, {
        'billing_text': 'Wasserabweisender Roll-Top Rucks',
        'channel_id': '1',
        'channeld_sku': '20919043',
        'created': FakeDatetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'date_created': datetime.datetime(2022, 9, 4, 19, 45, 43, tzinfo=datetime.timezone.utc),
        'ean': '0781491968887',
        'id': 3,
        'internal_status': 'IMPORTED',
        'item_price': Decimal('104.95'),
        'modified': FakeDatetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 2,
        'position_item_id': '531',
        'quantity': 1,
        'sku': 'ROLLTOP-MU',
        'transfer_price': Decimal('88.19')}]


def _prune_db():
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()


@freeze_time('2022-09-07')
@pytest.mark.django_db(reset_sequences=True)
def test_import_orders(client, django_user_model, pytestconfig):
    """XML from order file gets imported properly."""
    _prune_db()

    with open('mirapodo/tests/data/response_with_multiple_orders.xml', 'rb') as f:
        xml_string = f.read()

    # basic import
    parsed_order = xmltodict.parse(xml_string)
    import_orders(parsed_order)

    verify_addresses(Address.objects.all().values())
    verify_orders(Order.objects.all().values())
    verify_order_items(OrderItem.objects.all().values())

    # multiple import does not mess up things
    import_orders(parsed_order)
    import_orders(parsed_order)

    verify_addresses(Address.objects.all().values())
    verify_orders(Order.objects.all().values())
    verify_order_items(OrderItem.objects.all().values())

    # Download imported orders as CSV
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse('mirapodo_orderitems_csv')
    response = client.get(r_url)
    assert response.status_code == 200

    decoded_content = response.content.decode('utf-8')

    oi_csv_path = 'mirapodo/tests/data/orderitems.csv'
    if pytestconfig.getoption('--overwrite'):
        with open(oi_csv_path, 'w') as f:
            f.write(decoded_content)
        assert False, 'Mirapodo order items dump updated'

    with open(oi_csv_path, 'r') as oi_csv:
        expected = oi_csv.read()

    assert decoded_content.replace('\r', '') == expected


@freeze_time('2022-09-07')
@pytest.mark.django_db(reset_sequences=True)
def test_import_single_order():
    """XML from order file gets imported properly."""
    _prune_db()

    with open('mirapodo/tests/data/single_order.xml', 'rb') as f:
        xml_string = f.read()

    # basic import
    parsed_order = xmltodict.parse(xml_string)
    import_orders(parsed_order)

    assert [a for a in Address.objects.all().values()] == [{
        'addition': '2',
        'city': 'Ansbach',
        'country_code': 'DE',
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'first_name': 'Anna',
        'house_number': '8',
        'id': 1,
        'last_name': 'Muster',
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'street': 'Bahnhofsplatz',
        'title': 'Frau',
        'zip_code': '91522'
    }]

    assert [o for o in Order.objects.all().values()] == [{
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'delivery_address_id': 1,
        'delivery_fee': 'Hermes HSI',
        'id': 1,
        'internal_status': 'IMPORTED',
        'invoice_address_id': 1,
        'mail': 'Anna.muster@gmx.de',
        'marketplace_order_id': 'TB_2',
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_date': datetime.datetime(2021, 5, 7, 10, 32, 8, tzinfo=datetime.timezone.utc)
    }]

    assert [oi for oi in OrderItem.objects.all().values()] == [{
        'billing_text': 'Hardshelljacke',
        'channel_id': '4',
        'channeld_sku': '6947606427685',
        'created': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'date_created': datetime.datetime(2021, 5, 7, 10, 32, 8, tzinfo=datetime.timezone.utc),
        'ean': '6947606427685',
        'id': 1,
        'internal_status': 'IMPORTED',
        'item_price': Decimal('100.00'),
        'modified': datetime.datetime(2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc),
        'order_id': 1,
        'position_item_id': '2',
        'quantity': 1,
        'sku': 'women-bom-be-l',
        'transfer_price': Decimal('70.62')
    }]
