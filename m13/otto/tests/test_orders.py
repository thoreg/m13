import json
from unittest.mock import patch

import pytest
from django.urls import reverse
from freezegun import freeze_time

from core.models import Article, Product
from otto.models import Address, Order, OrderItem
from otto.services.orders import get_url, save_orders

FETCH_ORDERS_RESPONSE = './otto/tests/fixtures/fetch_orders_response.json'


@pytest.mark.django_db
@patch('otto.services.orders.fetch_orders_by_status')
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

    assert Product.objects.count() == 3
    assert Article.objects.count() == 3


test_data = [
    ('SENT', None, 'https://api.otto.market/v4/orders?fulfillmentStatus=SENT&fromOrderDate=2013-09-29T00%3A00%3A00%2B02%3A00'),
    ('PROCESSABLE', '2021-08-11', 'https://api.otto.market/v4/orders?fulfillmentStatus=PROCESSABLE&fromOrderDate=2021-08-11T00%3A00%3A00%2B02%3A00')
]


@freeze_time('2013-10-13')
@pytest.mark.parametrize("state,datum,expected_url", test_data)
def test_get_url(state, datum, expected_url):
    """Check all possible fullfillment states."""
    assert get_url(state, datum) == expected_url


OTTO_URLS = [
    'otto_orderitems_csv',
    'otto_import_orders',
    'otto_upload_tracking_codes_success',
    'otto_upload_tracking_codes',
    'otto_stats',
    'otto_index'
]


@pytest.mark.parametrize('otto_url', OTTO_URLS)
@pytest.mark.django_db
def test_otto_views(client, django_user_model, otto_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse(otto_url)
    response = client.get(r_url)
    assert response.status_code == 200
