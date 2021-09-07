
from decimal import Decimal

import pytest
from django.urls import reverse

from zalando.forms import PriceToolForm
from zalando.models import PriceTool

ZALANDO_URLS = [
    'zalando_index',
]


@pytest.mark.parametrize('z_url', ZALANDO_URLS)
@pytest.mark.django_db
def test_zalando_views(client, django_user_model, z_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(
        username=username, password=password)
    client.force_login(user)

    r_url = reverse(z_url)
    response = client.get(r_url)
    assert response.status_code == 200
    assert response.context['z_factor'] == 'UNDEFINED'
    assert isinstance(response.context['form'], PriceToolForm)

    pt = PriceTool.objects.create(z_factor=2, active=True)
    pt.save()

    response = client.get(r_url)
    assert response.status_code == 200
    assert response.context['z_factor'] == Decimal('2.00')
    assert isinstance(response.context['form'], PriceToolForm)
