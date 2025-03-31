from unittest.mock import patch

import pytest
from django.urls import reverse

from tiktok.services.orders import OrderService
from tiktok.services.stock import StockService

TIKTOK_URLS = [
    "tiktok_authcode",
    "tiktok_index",
    "tiktok_orderitems_csv",
    "tiktok_upload_tracking_codes_success",
    "tiktok_upload_tracking_codes",
]


@pytest.mark.parametrize("tiktok_url", TIKTOK_URLS)
@pytest.mark.django_db
def test_tiktok_views(client, django_user_model, tiktok_url):
    """Walk through existing views."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse(tiktok_url)
    response = client.get(r_url)
    assert response.status_code == 200


@patch("tiktok.services.stock.StockService.get_shop_cipher")
@patch("tiktok.services.stock.get_access_token")
@pytest.mark.django_db
def test_tiktok_services_stock(mock_get_access_token, mock_get_shop_cipher):
    """..."""
    StockService()
    mock_get_access_token.return_value = "foo"
    mock_get_shop_cipher.return_value = "bar"
    mock_get_access_token.assert_called_once()
    mock_get_shop_cipher.assert_called_once()


@patch("tiktok.services.orders.OrderService.get_shop_cipher")
@patch("tiktok.services.orders.get_access_token")
@pytest.mark.django_db
def test_tiktok_services_order(mock_get_access_token, mock_get_shop_cipher):
    """..."""
    OrderService()
    mock_get_access_token.return_value = "foo"
    mock_get_shop_cipher.return_value = "bar"
    mock_get_access_token.assert_called_once()
    mock_get_shop_cipher.assert_called_once()
