import json
from unittest.mock import patch

import pytest
from django.urls import reverse

ETSY_GET_URLS = [
    ('etsy_index', 200),
    ('etsy_oauth', 200),
    ('etsy_orders', 200),
]


@pytest.mark.parametrize('etsy_url_data', ETSY_GET_URLS)
@pytest.mark.django_db
def test_etsy_get_views(client, django_user_model, etsy_url_data):
    (etsy_url, expected_status_code) = etsy_url_data

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    with patch.dict('os.environ', {
            'M13_ETSY_API_KEY': 'foo',
            'M13_ETSY_OAUTH_REDIRECT': 'bar'}):
        r_url = reverse(etsy_url)
        response = client.get(r_url)
        assert response.status_code == expected_status_code
