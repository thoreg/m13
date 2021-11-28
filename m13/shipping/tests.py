import pytest
from django.urls import reverse

SHIPPING_URLS = [
    'upload_shipping_infos_success',
    'shipping_index'
]


@pytest.mark.parametrize('shipping_url', SHIPPING_URLS)
@pytest.mark.django_db
def test_shipping_views(client, django_user_model, shipping_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse(shipping_url)
    response = client.get(r_url)
    assert response.status_code == 200
