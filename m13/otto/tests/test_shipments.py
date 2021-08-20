from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from freezegun import freeze_time

from otto.models import Shipment
from otto.services.shipments import get_payload

SHIPMENTS_FILE = 'otto/tests/fixtures/Versandadressen.csv'


@pytest.mark.django_db
def test_handle_uploaded_file(client, django_user_model, django_db_setup):
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

        assert mocked_do_post.call_count == 3
        assert Shipment.objects.all().count() == 3


@freeze_time('2013-10-13')
@pytest.mark.django_db
def test_get_payload():
    payload = get_payload('8caf792f-7941-4d12-bc33-16db7199c42c', '123', 'Hurz')
    expected = {
        'trackingKey': {
            'carrier': 'Hurz', 'trackingNumber': '123'
        },
        'shipDate': '2013-10-13T00:00:00Z',
        'shipFromAddress': {
            'city': 'Hainburg',
            'countryCode': 'DEU',
            'zipCode': '63512'
        },
        'positionItems': [{
            'positionItemId': '31f53b49-caad-4b55-b925-706fe638ee8c',
            'salesOrderId': '8caf792f-7941-4d12-bc33-16db7199c42c',
            'returnTrackingKey': {
                'carrier': 'Hurz',
                'trackingNumber': '123'
            }
        }, {
            'positionItemId': 'fb917e1e-13a1-4549-a606-e47faea891a8',
            'salesOrderId': '8caf792f-7941-4d12-bc33-16db7199c42c',
            'returnTrackingKey': {
                'carrier': 'Hurz', 'trackingNumber': '123'
            }
        }]
    }
    assert payload == expected
