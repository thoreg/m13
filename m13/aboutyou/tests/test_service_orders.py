import csv
import json
import os
from unittest.mock import patch

import pytest
import requests
from django.urls import reverse
from freezegun import freeze_time

from aboutyou.models import Address, Order, OrderItem, Product
from aboutyou.services import orders


@freeze_time("2025-06-18")
@pytest.mark.django_db
def test_ay_orders_sync(client, django_user_model):
    """Basic order import creates Order and OrderItem objects."""

    Address.objects.all().delete()
    Order.objects.all().delete()
    OrderItem.objects.all().delete()

    Product.objects.create(sku="DEBUHA-BLU-SM", product_title="fake")

    os.environ["M13_ABOUTYOU_TOKEN"] = "bogus"

    with open(
        "aboutyou/tests/data/response_orders_1.json", "r", encoding="utf-8"
    ) as file:
        response_data1 = json.load(file)

    with open(
        "aboutyou/tests/data/response_orders_2.json", "r", encoding="utf-8"
    ) as file:
        response_data2 = json.load(file)

    with open(
        "aboutyou/tests/data/response_orders_3.json", "r", encoding="utf-8"
    ) as file:
        response_data3 = json.load(file)

    responses = [
        (response_data1["pagination"]["next"], response_data1["items"]),
        (response_data2["pagination"]["next"], response_data2["items"]),
        (response_data3["pagination"]["next"], response_data3["items"]),
    ]
    with (
        patch(
            "aboutyou.services.orders.download_orders",
            side_effect=responses,
        ) as _mocked_sync,
    ):

        orders.sync(Order.Status.OPEN)

    assert Address.objects.all().count() == 6
    assert Order.objects.all().count() == 6
    assert OrderItem.objects.all().count() == 7

    #
    # Check the CSV download based on the order import
    # There is only one orderitem in status 'open' in the fixtures
    #
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    response = client.get(reverse("ay_orderitems_csv"))

    assert response.status_code == requests.codes.ok
    decoded_content = response.content.decode("utf-8")
    download_data = csv.reader(decoded_content.splitlines(), delimiter=";")
    assert list(download_data) == [
        [
            "\ufeffBestellnummer",
            "Vorname",
            "Name",
            "Straße",
            "PLZ",
            "Ort",
            "Land",
            "Artikelnummer",
            "Artikelname",
            "Preis (Brutto)",
            "Menge",
            "Positionstyp",
            "Anmerkung",
            "EMAIL",
            "Auftragsdatum",
            "Adresszusatz",
        ],
        [
            "ayou-139-323979780",
            "Andreas",
            "Fuchs",
            "Wintercamp 77 ",
            "48653",
            "Koesfeld",
            "DE",
            "DEBUHA-BLU-SM",
            "fake",
            "34,95",
            "1",
            "Artikel",
            "ayou-139-323979780",
            "ay@manufaktur13.de",
            "18.06.25",
            "940639741",
        ],
        [
            "ayou-139-323979780",
            "Andreas",
            "Fuchs",
            "Wintercamp 77 ",
            "48653",
            "Koesfeld",
            "DE",
            " ",
            "DHL Paket (R)",
            "0",
            "1",
            "Versandposition",
            "ayou-139-323979780",
            "ay@manufaktur13.de",
            "18.06.25",
            "940639741",
        ],
    ]
