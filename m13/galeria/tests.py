import pytest
from django.urls import reverse

GALERIA_URLS = [
    "galeria_index",
    "galeria_price_feed",
]


@pytest.mark.parametrize("g_url", GALERIA_URLS)
@pytest.mark.django_db
def test_galeria_views(client, django_user_model, g_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse(g_url)
    response = client.get(r_url)
    assert response.status_code == 200
