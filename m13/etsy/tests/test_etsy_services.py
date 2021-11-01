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
