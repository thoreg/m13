import csv
import json
from unittest.mock import patch

import pytest
from django.urls import reverse
from freezegun import freeze_time

from etsy.models import Address, Order, OrderItem
from etsy.services import process_receipts

RECEIPTS_RESPONSE = './etsy/tests/fixtures/receipts.json'


@pytest.mark.django_db
@patch('etsy.services.get_receipts')
def test_process_receipts(mocked_fetch_orders):
    """Fetched orders are parsed and processes (stored)."""
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()

    with open(RECEIPTS_RESPONSE) as json_file:
        data = json.load(json_file)

    process_receipts(data)

    assert Address.objects.count() == 25
    assert Order.objects.count() == 25
    assert OrderItem.objects.count() == 28


@pytest.mark.django_db
def test_etsy_orderitems_csv(client, django_user_model):
    """Download orderitems plus shipping information as csv."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse('etsy_orderitems_csv')
    response = client.get(r_url)

    assert response.status_code == 200
    content = response.content.decode('utf-8-sig')

    # with open('etsy/tests/data/etsy_orderitems.csv', 'w') as oi_csv:
    #     oi_csv.write(content)
    with open('etsy/tests/data/etsy_orderitems.csv', 'r') as oi_csv:
        expected = oi_csv.read()

    assert content.replace('\r', '') == expected
