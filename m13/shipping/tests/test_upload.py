from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from core.models import Error
from mirapodo.models import Order as MirapodoOrder
from mirapodo.models import OrderItem as MirapodoOrderItem
from mirapodo.models import Shipment as MirapodoShipment
from otto.models import Shipment as OttoShipment

SHIPPING_URLS = ["upload_shipping_infos_success", "shipping_index"]

SHIPMENTS_FILE = "shipping/tests/data/Versandadressen.csv"


class MockResponse:
    def __init__(self, status_code, text):
        self.text = text
        self.status_code = status_code


@pytest.mark.parametrize("shipping_url", SHIPPING_URLS)
@pytest.mark.django_db
def test_shipping_views(client, django_user_model, shipping_url):
    """Simple test if urls are available and if views a rendered."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    r_url = reverse(shipping_url)
    response = client.get(r_url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_handle_uploaded_file(client, django_user_model):
    """Basic shipment file upload test."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    shipping_info_upload_url = reverse("shipping_index")
    response = client.get(shipping_info_upload_url)
    assert response.status_code == 200

    with open(SHIPMENTS_FILE, "rb") as csv_file:
        _file = SimpleUploadedFile(
            "upload.csv", csv_file.read(), content_type="text/csv"
        )

    with (
        patch(
            "otto.services.shipments.do_post", return_value=(201, {})
        ) as mocked_otto_do_post,
        patch(
            "mirapodo.services.shipments._post",
            return_value=MockResponse(201, "created"),
        ) as mocked_mirapodo_do_post,
    ):
        client.post(shipping_info_upload_url, {"file": _file}, format="multipart")

    # Verification OTTO
    otto_shipments = OttoShipment.objects.all()
    assert mocked_otto_do_post.call_count == 6
    assert [sh.tracking_info for sh in otto_shipments] == (
        [
            "04245181000623",
            "04245112000449",
            "04245166000365",
            "04245166000366",
            "04245166000367",
            "04245166000368",
        ]
    )
    assert [sh.response_status_code for sh in otto_shipments] == [
        201,
        201,
        201,
        201,
        201,
        201,
    ]

    # Verification MIRAPODO
    mirapodo_shipments = MirapodoShipment.objects.all()
    assert mocked_mirapodo_do_post.call_count == 2
    assert [sh.tracking_info for sh in mirapodo_shipments] == (
        [
            "01145166000368",
            "02245166000399",
        ]
    )
    assert [sh.response_status_code for sh in mirapodo_shipments] == [200, 200]

    mirapodo_orders = MirapodoOrder.objects.all()
    assert [o.internal_status for o in mirapodo_orders] == (
        [
            "IMPORTED",
            "IMPORTED",
            "SHIPPED",
            "SHIPPED",
        ]
    )

    mirapodo_orderitems = MirapodoOrderItem.objects.all().order_by("id")
    assert [oi.internal_status for oi in mirapodo_orderitems] == (
        [
            "SHIPPED",
            "SHIPPED",
            "IMPORTED",
            "IMPORTED",
            "SHIPPED",
        ]
    )

    errors = Error.objects.all().values()
    assert len(errors) == 2
    assert errors[0]["msg"].startswith("No auth token found: get_auth_token")
    assert errors[1]["msg"].startswith("No token found: handle_uploaded_file")
