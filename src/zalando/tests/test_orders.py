import pytest
from django.core.management import call_command

from zalando.models import Address, OEAWebhookMessage, Order, OrderItem
from zalando.services.orders import process_new_oea_records


def _load_fixture():
    Address.objects.all().delete()
    Order.objects.all().delete()
    OrderItem.objects.all().delete()
    OEAWebhookMessage.objects.all().delete()
    call_command("loaddata", "zalando/tests/fixtures/oea-msgs-small.fixture.json")


@pytest.mark.django_db
def test_process_new_oea_records_full_fixture():
    """Alle 6 Nachrichten (2 assigned, 2 fulfilled, 1 cancelled, 1 returned) korrekt verarbeitet."""
    _load_fixture()

    process_new_oea_records()

    assert Order.objects.filter(status="ASSIGNED").count() == 2
    assert Order.objects.filter(status="FULFILLED").count() == 2
    assert Order.objects.filter(status="CANCELLED").count() == 1
    assert Order.objects.filter(status="RETURNED").count() == 1
    assert OrderItem.objects.all().count() == 2
    assert Address.objects.all().count() == 2
    assert OEAWebhookMessage.objects.filter(processed=None).count() == 0


@pytest.mark.django_db
def test_process_new_oea_records_assigned_no_orderitems():
    """assigned-Event erzeugt Order, aber kein OrderItem und keine Adresse."""
    OEAWebhookMessage.objects.all().delete()
    Order.objects.all().delete()
    OEAWebhookMessage.objects.create(
        payload={
            "event_id": "test-assigned-001",
            "order_id": "test-order-assigned",
            "order_number": "99900000000001",
            "state": "assigned",
            "store_id": "001",
            "timestamp": "2021-09-15T09:00:00.000000Z",
            "items": [
                {
                    "item_id": "x",
                    "ean": "111",
                    "article_number": "A",
                    "currency": "EUR",
                    "price": 10.0,
                    "article_location": "M13",
                }
            ],
        }
    )

    process_new_oea_records()

    assert Order.objects.filter(status="ASSIGNED").count() == 1
    assert OrderItem.objects.all().count() == 0
    assert OEAWebhookMessage.objects.filter(processed=None).count() == 0


@pytest.mark.django_db
def test_process_new_oea_records_cancelled_returned_no_orderitems():
    """cancelled/returned erzeugen Order, aber kein OrderItem; alle als processed markiert."""
    OEAWebhookMessage.objects.all().delete()
    Order.objects.all().delete()

    for state, oid in [("cancelled", "test-order-c"), ("returned", "test-order-r")]:
        OEAWebhookMessage.objects.create(
            payload={
                "event_id": f"test-{state}",
                "order_id": oid,
                "order_number": f"999{state[:3]}",
                "state": state,
                "store_id": "001",
                "timestamp": "2021-09-17T10:00:00.000000Z",
                "items": [],
            }
        )

    process_new_oea_records()

    assert Order.objects.filter(status="CANCELLED").count() == 1
    assert Order.objects.filter(status="RETURNED").count() == 1
    assert OrderItem.objects.all().count() == 0
    assert OEAWebhookMessage.objects.filter(processed=None).count() == 0
