from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time

from otto.models import Order, Shipment
from otto.services.shipments import get_payload

SHIPMENTS_FILE = 'otto/tests/fixtures/Versandadressen.csv'


@pytest.mark.django_db
def test_handle_uploaded_file(client, django_user_model, django_db_setup):
    """Basic shipment file upload test."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)
    response = client.get('/otto/upload-tracking-codes/')
    assert response.status_code == 200

    with open(SHIPMENTS_FILE, 'rb') as csv_file:
        _file = SimpleUploadedFile(
            'upload.csv', csv_file.read(), content_type='text/csv')

    with patch(
            'otto.services.shipments.do_post',
            return_value=(201, {})) as mocked_do_post:

        response = client.post(
            '/otto/upload-tracking-codes/',
            {'file': _file},
            format='multipart'
        )

        shipments = Shipment.objects.all()
        assert mocked_do_post.call_count == 6
        assert len(shipments) == 6

    assert [sh.tracking_info for sh in shipments] == ([
        '04245181000623',
        '04245112000449',
        '04245166000365',
        '04245166000366',
        '04245166000367',
        '04245166000368'])

    assert [sh.response_status_code for sh in shipments] == [
        201, 201, 201, 201, 201, 201]


@freeze_time('2013-10-13')
@pytest.mark.django_db
def test_get_payload():
    """Generate proper payload for shipment update endpoint out of given order."""
    order = Order.objects.get(marketplace_order_number='bzyrxkr8mz')
    payload = get_payload(order, '123', 'Hurz')
    expected = {
        'trackingKey': {
            'carrier': 'Hurz', 'trackingNumber': '123'
        },
        'shipDate': '2013-10-13T00:00:00Z',
        'shipFromAddress': {
            'city': 'Berlin',
            'countryCode': 'DEU',
            'zipCode': '10365'
        },
        'positionItems': [{
            'positionItemId': '36c49130-759d-4e88-92d2-d14af26250a4',
            'salesOrderId': '239a3067-011f-4a5e-9a6c-7ddf4b2ff680',
            'returnTrackingKey': {
                'carrier': 'Hurz',
                'trackingNumber': '123'
            }
        }]
    }
    assert payload == expected
