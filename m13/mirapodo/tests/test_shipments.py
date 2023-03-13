import json
from unittest.mock import patch

import pytest

from mirapodo.models import Order, OrderItem
from mirapodo.services.orders import import_orders
from mirapodo.services.shipments import upload_tracking_info


class MockResponse:
    def __init__(self, status_code, text):
        self.text = text
        self.status_code = status_code


def _clean_db():
    OrderItem.objects.all().delete()
    Order.objects.all().delete()


@pytest.mark.django_db
def test_upload_tracking_info(httpbin):
    """Upload of tracking information for different scenarios."""
    _clean_db()

    #
    # 0 - Single Order - Quantity 1
    #
    with open("mirapodo/tests/data/single_order.json", "r") as f:
        parsed_single_order = json.load(f)
    import_orders(parsed_single_order)

    assert Order.objects.all().count() == 1
    assert OrderItem.objects.all().count() == 1

    oi = OrderItem.objects.get()
    assert oi.internal_status == OrderItem.Status.IMPORTED

    order = Order.objects.get()
    with patch("mirapodo.services.shipments._post") as mock_post:
        mock_post.return_value = MockResponse(200, "success")
        upload_tracking_info(order, "1234321")

    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["data"] == (
        '<?xml version="1.0" encoding="utf-8"?><MESSAGES_LIST><MESSAGE>'
        "<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>"
        "<TB_ORDER_ID>489</TB_ORDER_ID>"
        "<TB_ORDER_ITEM_ID>623</TB_ORDER_ITEM_ID>"
        "<SKU>women-bom-da-xs</SKU>"
        "<QUANTITY>1</QUANTITY>"
        "<CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE>"
        "<IDCODE>1234321</IDCODE>"
        "<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL></MESSAGE></MESSAGES_LIST>"
    )
    oi = OrderItem.objects.get()
    assert oi.internal_status == OrderItem.Status.SHIPPED

    _clean_db()

    #
    # 1 - Single Order - Quantity 3
    #
    with open("mirapodo/tests/data/single_order.json", "r") as f:
        parsed_single_order = json.load(f)
    parsed_single_order["ORDER_LIST"]["ORDER"]["ITEMS"]["ITEM"]["QUANTITY"] = 3
    import_orders(parsed_single_order)

    assert Order.objects.all().count() == 1
    assert OrderItem.objects.all().count() == 1

    oi = OrderItem.objects.get()
    assert oi.internal_status == OrderItem.Status.IMPORTED

    order = Order.objects.get()
    with patch("mirapodo.services.shipments._post") as mock_post:
        mock_post.return_value = MockResponse(200, "success")
        upload_tracking_info(order, "1234321")

    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["data"] == (
        '<?xml version="1.0" encoding="utf-8"?><MESSAGES_LIST><MESSAGE>'
        "<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>"
        "<TB_ORDER_ID>489</TB_ORDER_ID>"
        "<TB_ORDER_ITEM_ID>623</TB_ORDER_ITEM_ID>"
        "<SKU>women-bom-da-xs</SKU>"
        "<QUANTITY>3</QUANTITY>"
        "<CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE>"
        "<IDCODE>1234321</IDCODE>"
        "<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL></MESSAGE></MESSAGES_LIST>"
    )
    oi = OrderItem.objects.get()
    assert oi.internal_status == OrderItem.Status.SHIPPED

    _clean_db()

    #
    # 2 - Multi Order
    #
    with open("mirapodo/tests/data/multi_order.json", "r") as f:
        parsed_multi_order = json.load(f)
    import_orders(parsed_multi_order)

    assert Order.objects.all().count() == 1
    assert OrderItem.objects.all().count() == 3
    assert (
        OrderItem.objects.filter(internal_status=OrderItem.Status.IMPORTED).count() == 3
    )
    assert (
        OrderItem.objects.filter(internal_status=OrderItem.Status.SHIPPED).count() == 0
    )

    order = Order.objects.get()
    with patch("mirapodo.services.shipments._post") as mock_post:
        mock_post.return_value = MockResponse(200, "success")
        upload_tracking_info(order, "1234321")

    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["data"] == (
        '<?xml version="1.0" encoding="utf-8"?><MESSAGES_LIST><MESSAGE>'
        "<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>"
        "<TB_ORDER_ID>479</TB_ORDER_ID>"
        "<TB_ORDER_ITEM_ID>609</TB_ORDER_ITEM_ID>"
        "<SKU>BM013-FBM</SKU>"
        "<QUANTITY>1</QUANTITY>"
        "<CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE>"
        "<IDCODE>1234321</IDCODE>"
        "<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL>"
        "</MESSAGE>"
        "<MESSAGE>"
        "<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>"
        "<TB_ORDER_ID>479</TB_ORDER_ID>"
        "<TB_ORDER_ITEM_ID>611</TB_ORDER_ITEM_ID>"
        "<SKU>SM010</SKU>"
        "<QUANTITY>1</QUANTITY>"
        "<CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE>"
        "<IDCODE>1234321</IDCODE>"
        "<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL>"
        "</MESSAGE>"
        "<MESSAGE>"
        "<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>"
        "<TB_ORDER_ID>479</TB_ORDER_ID>"
        "<TB_ORDER_ITEM_ID>613</TB_ORDER_ITEM_ID>"
        "<SKU>KLOOP-MU</SKU>"
        "<QUANTITY>1</QUANTITY>"
        "<CARRIER_PARCEL_TYPE>DHL_STD_NATIONAL</CARRIER_PARCEL_TYPE>"
        "<IDCODE>1234321</IDCODE>"
        "<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL>"
        "</MESSAGE></MESSAGES_LIST>"
    )
    assert (
        OrderItem.objects.filter(internal_status=OrderItem.Status.IMPORTED).count() == 0
    )
    assert (
        OrderItem.objects.filter(internal_status=OrderItem.Status.SHIPPED).count() == 3
    )
