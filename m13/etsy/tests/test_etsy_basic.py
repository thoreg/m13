import json
from unittest.mock import patch

import pytest
from django.urls import reverse
from freezegun import freeze_time

ETSY_GET_URLS = [
    'etsy_index',
    'etsy_oauth',
    'etsy_orders',
]


@pytest.mark.parametrize('etsy_url', ETSY_GET_URLS)
@pytest.mark.django_db
def test_etsy_get_views(client, django_user_model, etsy_url):
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
        assert response.status_code == 200
