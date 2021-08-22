import json
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from otto.models import Address, Order, OrderItem
from otto.services.orders import get_url, save_orders

FETCH_ORDERS_RESPONSE = './otto/tests/fixtures/fetch_orders_response.json'


@pytest.mark.django_db
@patch('otto.services.orders.fetch_orders')
def test_save_orders(mocked_fetch_orders):
    """Fetched orders are parsed and processes (stored)."""

    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()

    with open(FETCH_ORDERS_RESPONSE) as json_file:
        data = json.load(json_file)

    save_orders(data)

    assert Address.objects.count() == 2
    assert Order.objects.count() == 2
    assert OrderItem.objects.count() == 3

    assert OrderItem.objects.filter(fulfillment_status='RETURNED').count() == 2
    assert OrderItem.objects.filter(fulfillment_status='SENT').count() == 1


test_data = [
    ('SENT', None, 'https://api.otto.market/v4/orders?fulfillmentStatus=SENT&fromOrderDate=2013-10-08T00%3A00%3A00%2B02%3A00'),
    ('PROCESSABLE', '2021-08-11', 'https://api.otto.market/v4/orders?fulfillmentStatus=PROCESSABLE&fromOrderDate=2021-08-11T00%3A00%3A00%2B02%3A00')
]


@freeze_time('2013-10-13')
@pytest.mark.parametrize("state,datum,expected_url", test_data)
def test_get_url(state, datum, expected_url):
    """Check all possible fullfillment states."""
    assert get_url(state, datum) == expected_url
