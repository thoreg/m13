import pytest
from freezegun import freeze_time

from otto.models import Order
from otto.services.shipments import get_payload


@freeze_time("2013-10-13")
@pytest.mark.django_db
def test_get_payload():
    """Generate proper payload for shipment update endpoint out of given order."""
    order = Order.objects.get(marketplace_order_number="bzyrxkr8mz")
    payload = get_payload(order, "123", "Hurz")
    expected = {
        "trackingKey": {"carrier": "Hurz", "trackingNumber": "123"},
        "shipDate": "2013-10-13T00:00:00Z",
        "shipFromAddress": {"city": "Berlin", "countryCode": "DEU", "zipCode": "10365"},
        "positionItems": [
            {
                "positionItemId": "36c49130-759d-4e88-92d2-d14af26250a4",
                "salesOrderId": "239a3067-011f-4a5e-9a6c-7ddf4b2ff680",
                "returnTrackingKey": {"carrier": "Hurz", "trackingNumber": "123"},
            }
        ],
    }
    assert payload == expected
