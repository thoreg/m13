import json
from unittest.mock import MagicMock, patch

import pytest

from otto.models import Address, Order, OrderItem
from otto.services.orders import get_orders

FETCH_ORDERS_RESPONSE = './otto/tests/fixtures/fetch_orders_response.json'

@pytest.mark.django_db
@patch('otto.services.orders.fetch_orders')
def test_get_orders(mocked_fetch_orders):
    """Fetched orders are parsed and processes (stored)."""
    with open(FETCH_ORDERS_RESPONSE) as json_file:
        data = json.load(json_file)
    mocked_fetch_orders.return_value = data

    get_orders('SENT', '2021-08-11T00:00:00+00:00')

    assert Address.objects.count() == 2
    assert Order.objects.count() == 2
    assert OrderItem.objects.count() == 3

    assert OrderItem.objects.filter(fulfillment_status='RETURNED').count() == 2
    assert OrderItem.objects.filter(fulfillment_status='SENT').count() == 1
