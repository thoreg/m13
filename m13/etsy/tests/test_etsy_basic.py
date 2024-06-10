from unittest.mock import patch

import pytest
from django.urls import reverse

from etsy.models import Address

ETSY_GET_URLS = [
    ("etsy_index", 200),
    ("etsy_oauth", 200),
    ("etsy_orders", 200),
]


@pytest.mark.parametrize("etsy_url_data", ETSY_GET_URLS)
@pytest.mark.django_db
def test_etsy_get_views(client, django_user_model, etsy_url_data):
    (etsy_url, expected_status_code) = etsy_url_data

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    with patch.dict(
        "os.environ", {"M13_ETSY_API_KEY": "foo", "M13_ETSY_OAUTH_REDIRECT": "bar"}
    ):
        r_url = reverse(etsy_url)
        response = client.get(r_url)
        assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_address_get_address_as_columns():
    """Return proper first and surname and rest of address"""
    address, _created = Address.objects.get_or_create(
        buyer_email="bla@blub.de",
        buyer_user_id=1,
        city="SCHÖLLNACH",
        country_code="DE",
        formatted_address="""Julia Alexandra Hartmann
        Ammanger Str.77
        94508 SCHÖLLNACH
        Germany
        """,
        zip_code="94508",
    )

    first_name, last_name, address_part = address.get_address_as_columns()

    assert first_name == "Julia Alexandra"
    assert last_name == "Hartmann"
    assert address_part == "Ammanger Str.77"


TEST_DATA = [
    # (formatted_address, expected_first_name, expected_last_name, expected_street)
    (
        """Schmukas Schatzi Benetsborgaro
        Ulrichsberger Straße 123
        Fivethousandfingergames GmbH
        94469 DEGGENDORF
        Germany""",
        "Schmukas Schatzi",
        "Benetsborgaro",
        "Ulrichsberger Straße 123\nFivethousandfingergames GmbH",
    ),
    (
        """Stefanie Mechaelis
        Kollererstraße 217 a
        82256 FÜRSTENFELDBRUCK
        Germany""",
        "Stefanie",
        "Mechaelis",
        "Kollererstraße 217 a",
    ),
    (
        """Nomia Tirsoni
        Brüniggerstr. 146
        6053 Alpnachstad
        Switzerland""",
        "Nomia",
        "Tirsoni",
        "Brüniggerstr. 146",
    ),
    (
        """Sandro Reskoni
        Lombertstr.
        15
        53721 SIEGBURG
        Germany""",
        "Sandro",
        "Reskoni",
        "Lombertstr. 15",
    ),
    (
        """Sarah Zoe Tobiaschischi
        Neuer Berg 181
        69226 NUSSLOCH
        Germany""",
        "Sarah Zoe",
        "Tobiaschischi",
        "Neuer Berg 181",
    ),
    (
        """Fiasi Themser
        Glockerstr. 152D
        22081 HAMBURG
        Germany""",
        "Fiasi",
        "Themser",
        "Glockerstr. 152D",
    ),
    (
        """Selin Trümmel
        Neckartalstr.551
        12053 BERLIN
        Germany""",
        "Selin",
        "Trümmel",
        "Neckartalstr.551",
    ),
    (
        """Elfi Horn
        Veilchenstr, 123
        Frau
        72285 PFALZGRAFENWEILER
        Germany""",
        "Elfi",
        "Horn",
        "Veilchenstr, 123 Frau",
    ),
    (
        """Roberto Tardennoni
        Schützenstr.
        121
        88709 MEERSBURG
        Germany""",
        "Roberto",
        "Tardennoni",
        "Schützenstr. 121",
    ),
    (
        """Martin Kundari
        Packstation 405
        8204269997
        10559 BERLIN
        Germany""",
        "Martin",
        "Kundari",
        "Packstation 405\n8204269997",
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "formatted_address,expected_first_name,expected_last_name,expected_street",
    TEST_DATA,
)
def test_extended_address_as_columns(
    formatted_address, expected_first_name, expected_last_name, expected_street
):
    """Return proper first and surname and rest of address"""
    address, _created = Address.objects.get_or_create(
        buyer_email="bla@blub.de",
        buyer_user_id=1,
        city="SCHÖLLNACH",
        country_code="DE",
        formatted_address=formatted_address,
        zip_code="94508",
    )

    first_name, last_name, address_part = address.get_address_as_columns()

    assert first_name == expected_first_name
    assert last_name == expected_last_name
    assert address_part == expected_street
