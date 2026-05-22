"""Tests for irisone.services.orders."""

import pytest

from irisone.models import Order, OrderLine
from irisone.services.orders import _upsert_order, _upsert_lines


ORDER_DATA = {
    "booking_id": 1001,
    "order_id": 2001,
    "marketplace_name": "zalando",
    "marketplace_detail": "zalando-de",
    "marketplace_order_id_1": "abc-123",
    "marketplace_order_id_2": None,
    "order_date": "2026-05-22T10:00:00.000000Z",
    "currency": "EUR",
    "buyer_country": "DE",
    "status": "pending",
    "exported": False,
    "origin_labels": "external",
    "origin_documents": "external",
    "origin_invoices": "external",
}

LINES_DATA = [
    {
        "line_id": 501,
        "item_id": 601,
        "line_identifier": "line-uuid-001",
        "marketplace_sku": "M13-SKU-001",
        "price": "49.9",
        "price_net": "41.93",
        "vat": "19.0",
        "status": "pending",
        "erp_additions": {"erp_id": "SKU-001"},
    }
]


@pytest.mark.django_db
def test_upsert_order_creates_new():
    order, created = _upsert_order(ORDER_DATA)
    assert created is True
    assert order.booking_id == 1001
    assert order.marketplace_name == "zalando"
    assert order.status == Order.Status.PENDING


@pytest.mark.django_db
def test_upsert_order_idempotent():
    _upsert_order(ORDER_DATA)
    order, created = _upsert_order(ORDER_DATA)
    assert created is False
    assert Order.objects.filter(booking_id=1001).count() == 1


@pytest.mark.django_db
def test_upsert_order_updates_status():
    _upsert_order(ORDER_DATA)
    updated_data = {**ORDER_DATA, "status": "opened"}
    order, created = _upsert_order(updated_data)
    assert created is False
    assert order.status == Order.Status.OPENED


@pytest.mark.django_db
def test_upsert_lines_creates_lines():
    order, _ = _upsert_order(ORDER_DATA)
    count = _upsert_lines(order, LINES_DATA)
    assert count == 1
    line = OrderLine.objects.get(line_id=501)
    assert line.order == order
    assert line.article_number == "SKU-001"
    assert line.price == "49.9"


@pytest.mark.django_db
def test_upsert_lines_idempotent():
    order, _ = _upsert_order(ORDER_DATA)
    _upsert_lines(order, LINES_DATA)
    count = _upsert_lines(order, LINES_DATA)
    assert count == 0
    assert OrderLine.objects.filter(order=order).count() == 1
