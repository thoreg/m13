import pytest
from django.core.management import call_command


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Initial db setup for integration tests."""
    fixtures = [
        "otto/tests/fixtures/address.json",
        "otto/tests/fixtures/order.json",
        "otto/tests/fixtures/order_item.json",
        "zalando/tests/fixtures/oea_webhook_messages.fixture.json",
        "etsy/tests/fixtures/etsy.address.json",
        "etsy/tests/fixtures/etsy.order.json",
        "etsy/tests/fixtures/etsy.orderitem.json",
        "mirapodo/tests/fixtures/mirapodo.address.yaml",
        "mirapodo/tests/fixtures/mirapodo.order.yaml",
        "mirapodo/tests/fixtures/mirapodo.orderitem.yaml",
    ]
    with django_db_blocker.unblock():
        for fixture in fixtures:
            call_command("loaddata", fixture)


def pytest_addoption(parser):
    """Add optparse-style options."""
    parser.addoption(
        "--overwrite",
        action="store_true",
        help="Overwrite regression test traces (tests will fail then!)",
    )
