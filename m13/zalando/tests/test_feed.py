from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import Error
from zalando.forms import PriceToolForm
from zalando.models import PriceTool

ZALANDO_URLS = [
    "zalando_price_feed",
    "zalando_index",
    "zalando_finance_upload_files",
    "zalando_finance_calculator_v1",
]


@pytest.mark.parametrize("z_url", ZALANDO_URLS)
@pytest.mark.django_db
def test_zalando_views(client, django_user_model, z_url):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse(z_url)
    response = client.get(r_url)
    assert response.status_code == 200

    if not z_url == "zalando_price_feed":
        return

    assert response.context["z_factor"] == "UNDEFINED"
    assert isinstance(response.context["form"], PriceToolForm)

    pt = PriceTool.objects.create(z_factor=2, active=True)
    pt.save()

    response = client.get(r_url)
    assert response.status_code == 200
    assert response.context["z_factor"] == Decimal("2.00")
    assert isinstance(response.context["form"], PriceToolForm)


@pytest.mark.django_db
def test_zalando_oem_endpoint(client, django_user_model, settings):
    Error.objects.all().delete()

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse("zalando_oea_webhook")

    # GET instead of POST
    response = client.get(r_url)
    assert response.status_code == 405
    assert response.reason_phrase == "Method Not Allowed"

    # POST but token not defined
    response = client.post(r_url, HTTP_X_API_KEY="123")
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.content == b"Incorrect token in header"

    # POST - token defined but wrong given
    settings.ZALANDO_OEM_WEBHOOK_TOKEN = "1234"
    response = client.post(r_url, HTTP_X_API_KEY="123")
    assert response.status_code == 403
    assert response.reason_phrase == "Forbidden"
    assert response.content == b"Incorrect token in header"

    # POST - token defined - right taken given - no JSON
    settings.ZALANDO_OEM_WEBHOOK_TOKEN = "1234"
    response = client.post(r_url, HTTP_X_API_KEY="1234")
    assert response.status_code == 200
    assert response.content == b"Request body is not JSON"

    # POST - token defined - right taken given - no JSON
    settings.ZALANDO_OEM_WEBHOOK_TOKEN = "1234"
    response = client.post(
        r_url, {"foo": "bar"}, content_type="application/json", HTTP_X_API_KEY="1234"
    )
    assert response.status_code == 200
    assert response.content == b"Message received okay."

    assert Error.objects.all().count() == 1
