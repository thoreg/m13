
import pytest

from mirapodo.models import Order
from mirapodo.services.shipments import get_payload


@pytest.mark.django_db
def test_get_payload():
    """Right payload data is created from order+tracking_info."""
    order = Order.objects.all().order_by('-order_date')[0]

    payload = get_payload(order, 12345)

    assert payload == (
        '<?xml version="1.0" encoding="utf-8"?><MESSAGES_LIST><MESSAGE>'
        '<MESSAGE_TYPE>SHIP</MESSAGE_TYPE>'
        '<TB_ORDER_ID>431</TB_ORDER_ID>'
        '<TB_ORDER_ITEM_ID>553</TB_ORDER_ITEM_ID>'
        '<SKU>KLOOP-BO</SKU>'
        '<QUANTITY>1</QUANTITY>'
        '<CARRIER_PARCEL_TYPE>HERMES_STD_NATIONAL</CARRIER_PARCEL_TYPE>'
        '<IDCODE>12345</IDCODE>'
        '<IDCODE_RETURN_PROPOSAL>1</IDCODE_RETURN_PROPOSAL></MESSAGE></MESSAGES_LIST>'
    )
