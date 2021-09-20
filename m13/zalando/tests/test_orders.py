import pytest
from django.core.management import call_command

from zalando.models import Address, OEAWebhookMessage, Order, OrderItem
from zalando.services.orders import process_new_oea_records


@pytest.mark.django_db
def test_process_new_oea_records(django_db_setup):
    """..."""

    process_new_oea_records()

    assert Order.objects.all().count() == 58
    assert OrderItem.objects.all().count() == 73
    assert Address.objects.all().count() == 48


@pytest.mark.django_db
def test_process_oea_records_detail():
    """..."""
    Address.objects.all().delete()
    Order.objects.all().delete()
    OrderItem.objects.all().delete()
    OEAWebhookMessage.objects.all().delete()

    call_command(
        'loaddata', 'zalando/tests/fixtures/oea-msgs-small.fixture.json')

    process_new_oea_records()

    assert Order.objects.all().count() == 6
    assert OrderItem.objects.all().count() == 3
    assert Address.objects.all().count() == 3
