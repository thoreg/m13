from unittest.mock import patch

import pytest
from django.urls import reverse

AY_GET_URLS = [
    ("ay_index", 200),
    ("ay_import_orders", 200),
    ("ay_orderitems_csv", 200),
    ("ay_upload_tracking_codes_success", 200),
    ("ay_upload_tracking_codes", 200),
]


@pytest.mark.parametrize("ay_url_data", AY_GET_URLS)
@pytest.mark.django_db
def test_ay_get_views(client, django_user_model, ay_url_data):
    (ay_url, expected_status_code) = ay_url_data

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse(ay_url)

    with (
        patch(
            "aboutyou.services.orders.sync",
            return_value="bogus",
        ) as _mocked_sync,
    ):

        response = client.get(r_url)
        assert response.status_code == expected_status_code
