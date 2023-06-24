import datetime
from decimal import Decimal

import pytest
from freezegun import freeze_time

from galaxus.models import Address, Order, OrderItem
from galaxus.services.orders import import_orders


def _prune_db():
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Address.objects.all().delete()


@freeze_time("2022-09-07")
@pytest.mark.django_db(reset_sequences=True)
def test_galaxus_import_orders(client, django_user_model, pytestconfig):
    """XML from order file gets imported properly."""
    _prune_db()

    with open("galaxus/tests/data/address_private_customer.xml", "rb") as f:
        xml_string = f.read()

    import_orders(xml_string)

    addresses = Address.objects.all().values()
    orders = Order.objects.all().values()
    ois = OrderItem.objects.all().values()

    assert [a for a in addresses] == [
        {
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "city": "Spreitenach",
            "country_code": "Schweiz",
            "first_name": "Ver 2.0 Richard & Annelie’s",
            "id": 1,
            "last_name": "Kaufmann+Meiermann Co.",
            "street": "Bei der Kaufmannstrasse 3",
            "title": "Herr",
            "zip_code": "9999",
        }
    ]
    assert [o for o in orders] == [
        {
            "id": 1,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "marketplace_order_id": "61730204",
            "marketplace_order_number": "",
            "order_date": datetime.datetime(
                2022, 3, 28, 9, 31, 19, tzinfo=datetime.timezone.utc
            ),
            "invoice_address_id": 1,
            "delivery_address_id": 1,
            "internal_status": "IMPORTED",
            "delivery_fee": "DHL Paket (R)",
            "mail": "spmpartnerresponses@digitecgalaxus.ch",
        }
    ]
    assert [oi for oi in ois] == [
        {
            "id": 1,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "order_id": 1,
            "cancellation_date": None,
            "expected_delivery_date": datetime.datetime(
                2022, 7, 19, 22, 0, tzinfo=datetime.timezone.utc
            ),
            "fulfillment_status": "",
            "price": Decimal("1390.33"),
            "quantity": 1,
            "position_item_id": "1",
            "ean": "00889842737240",
            "product_title": 'Microsoft Surface Laptop 4 (13.50 ", Intel Core i7-1185G7, 16 GB, 512 GB)',
            "sku": "4135378",
            "returned_date": None,
            "sent_date": None,
            "carrier": None,
            "carrier_service_code": None,
            "tracking_number": None,
        }
    ]

    _prune_db()

    with open(
        "galaxus/tests/data/address_private_customer_with_company_address.xml", "rb"
    ) as f:
        xml_string = f.read()

    import_orders(xml_string)

    addresses = Address.objects.all().values()
    orders = Order.objects.all().values()
    ois = OrderItem.objects.all().values()

    assert [a for a in addresses] == [
        {
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "city": "Testort in Zürich West (Firmenadresse Privatkunde)",
            "country_code": "Schweiz",
            "first_name": "Ver 2.0 Firma der Richi Verlagsgesellschafterei AG\n"
            "Richard Meier’s privates Ablagefach der Blockchain",
            "id": 2,
            "last_name": "Im Westpartk Nord-West im 5. Stockwerk Lift rechts",
            "street": "Bei der Kaufmannstrasse 3",
            "title": "",
            "zip_code": "0000",
        }
    ]
    assert [o for o in orders] == [
        {
            "id": 2,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "marketplace_order_id": "61730211",
            "marketplace_order_number": "",
            "order_date": datetime.datetime(
                2022, 3, 28, 9, 55, 29, tzinfo=datetime.timezone.utc
            ),
            "invoice_address_id": 2,
            "delivery_address_id": 2,
            "internal_status": "IMPORTED",
            "delivery_fee": "DHL Paket (R)",
            "mail": "spmpartnerresponses@digitecgalaxus.ch",
        }
    ]
    assert [oi for oi in ois] == [
        {
            "id": 2,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "order_id": 2,
            "cancellation_date": None,
            "expected_delivery_date": datetime.datetime(
                2022, 7, 19, 22, 0, tzinfo=datetime.timezone.utc
            ),
            "fulfillment_status": "",
            "price": Decimal("1390.33"),
            "quantity": 1,
            "position_item_id": "1",
            "ean": "00889842737240",
            "product_title": 'Microsoft Surface Laptop 4 (13.50 ", Intel Core i7-1185G7, 16 GB, 512 GB)',
            "sku": "4135378",
            "returned_date": None,
            "sent_date": None,
            "carrier": None,
            "carrier_service_code": None,
            "tracking_number": None,
        }
    ]

    _prune_db()

    with open("galaxus/tests/data/address_business_customer.xml", "rb") as f:
        xml_string = f.read()

    import_orders(xml_string)

    addresses = Address.objects.all().values()
    orders = Order.objects.all().values()
    ois = OrderItem.objects.all().values()

    assert [a for a in addresses] == [
        {
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "city": "Musterhausen",
            "country_code": "Schweiz",
            "first_name": "Peter",
            "id": 3,
            "last_name": "Meier",
            "street": "Bei der Kaufmannstrasse 3",
            "title": "",
            "zip_code": "0000",
        }
    ]
    assert [o for o in orders] == [
        {
            "id": 3,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "marketplace_order_id": "61730220",
            "marketplace_order_number": "",
            "order_date": datetime.datetime(
                2022, 3, 28, 11, 10, 7, tzinfo=datetime.timezone.utc
            ),
            "invoice_address_id": 3,
            "delivery_address_id": 3,
            "internal_status": "IMPORTED",
            "delivery_fee": "DHL Paket (R)",
            "mail": "spmpartnerresponses@digitecgalaxus.ch",
        }
    ]
    assert [oi for oi in ois] == [
        {
            "id": 3,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "order_id": 3,
            "cancellation_date": None,
            "expected_delivery_date": datetime.datetime(
                2022, 7, 19, 22, 0, tzinfo=datetime.timezone.utc
            ),
            "fulfillment_status": "",
            "price": Decimal("1390.33"),
            "quantity": 1,
            "position_item_id": "1",
            "ean": "00889842737240",
            "product_title": 'Microsoft Surface Laptop 4 (13.50 ", Intel Core i7-1185G7, 16 GB, 512 GB)',
            "sku": "4135378",
            "returned_date": None,
            "sent_date": None,
            "carrier": None,
            "carrier_service_code": None,
            "tracking_number": None,
        },
        {
            "cancellation_date": None,
            "carrier": None,
            "carrier_service_code": None,
            "created": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "ean": "04064575370124",
            "expected_delivery_date": datetime.datetime(
                2022, 4, 4, 22, 0, tzinfo=datetime.timezone.utc
            ),
            "fulfillment_status": "",
            "id": 4,
            "modified": datetime.datetime(
                2022, 9, 7, 0, 0, tzinfo=datetime.timezone.utc
            ),
            "order_id": 3,
            "position_item_id": "2",
            "price": Decimal("4086.14"),
            "product_title": 'Apple MacBook Pro – Late 2021 (14 ", M1 Max, 64 GB, 4000 '
            "GB)",
            "quantity": 1,
            "returned_date": None,
            "sent_date": None,
            "sku": "4347777",
            "tracking_number": None,
        },
    ]
