import pytest
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    fixtures = [
        'otto/tests/fixtures/address.json',
        'otto/tests/fixtures/order.json',
        'otto/tests/fixtures/order_item.json',
        'zalando/tests/fixtures/oea_webhook_messages.fixture.json'
    ]
    with django_db_blocker.unblock():
        for fixture in fixtures:
            call_command('loaddata', fixture)
