"""Import Orders from marketplace Galaxus"""

import logging
import os
from decimal import Decimal

import paramiko
import xmltodict

from galaxus.models import Address, Order, OrderItem

DELIVERY_FEE_STANDARD = "DHL Paket (R)"

LOG = logging.getLogger(__name__)

M13_GALAXUS_FTP_SERVER = os.getenv("M13_GALAXUS_FTP_SERVER", "")
M13_GALAXUS_FTP_USER = os.getenv("M13_GALAXUS_FTP_USER", "")
M13_GALAXUS_FTP_PASSWORD = os.getenv("M13_GALAXUS_FTP_PASSWORD", "")


def import_orders(good_old_xml):
    """Parse the good old XML provided via ftp from good old Galaxus and import the order(s)."""
    parsed_order = xmltodict.parse(good_old_xml)

    delivery_xml = [
        p
        for p in parsed_order["ORDER"]["ORDER_HEADER"]["ORDER_INFO"]["PARTIES"]["PARTY"]
        if p["PARTY_ROLE"] == "delivery"
    ]
    address_dict = delivery_xml[0]

    address_data = address_dict.get("ADDRESS")
    order_data = parsed_order.get("ORDER")

    #
    # 'ORDER_SUMMARY': {'TOTAL_AMOUNT': '1390.33', 'TOTAL_ITEM_NUM': '1'}}}
    order_summary = order_data.get("ORDER_SUMMARY")
    LOG.info(order_summary)

    try:
        title = address_data.get("CONTACT_DETAILS").get("TITLE").get("#text")
    except AttributeError:
        title = ""

    try:
        # Private customer
        first_name = address_data.get("CONTACT_DETAILS").get("FIRST_NAME").get("#text")
        last_name = address_data.get("CONTACT_DETAILS").get("CONTACT_NAME").get("#text")

    except AttributeError:
        # Private customer with company address
        # 'NAME': {'#text': 'Ver 2.0 Firma der Richi Verlagsgesellschafterei AG',
        #     '@xmlns': 'http://www.bmecat.org/bmecat/2005'},
        # 'NAME2': {'#text': 'Richard Meier’s privates Ablagefach der Blockchain',
        #         '@xmlns': 'http://www.bmecat.org/bmecat/2005'},
        # 'NAME3': {'#text': 'Im Westpartk Nord-West im 5. Stockwerk Lift rechts',
        #         '@xmlns': 'http://www.bmecat.org/bmecat/2005'},
        name = address_data.get("NAME").get("#text")
        name2 = address_data.get("NAME2").get("#text")
        name3 = address_data.get("NAME3").get("#text")
        first_name = f"{name}\n{name2}"
        last_name = f"{name3}"

    delivery_address, _created = Address.objects.get_or_create(
        first_name=first_name,
        last_name=last_name,
        city=address_data.get("CITY").get("#text"),
        country_code=address_data.get("COUNTRY").get("#text"),
        street=address_data.get("STREET").get("#text"),
        title=title,
        zip_code=address_data.get("ZIP").get("#text"),
    )

    order_info = order_data.get("ORDER_HEADER").get("ORDER_INFO")
    marketplace_order_id = order_info.get("ORDER_ID")
    order, created = Order.objects.get_or_create(
        marketplace_order_id=marketplace_order_id,
        defaults={
            "delivery_address": delivery_address,
            "delivery_fee": DELIVERY_FEE_STANDARD,
            "invoice_address": delivery_address,
            "order_date": order_info.get("ORDER_DATE"),
            "mail": address_data.get("EMAIL", "not_available@manufaktur13.de").get(
                "#text"
            ),
        },
    )
    if created:
        LOG.info(f"Order {marketplace_order_id} imported")

    else:
        LOG.info(f"Order {marketplace_order_id} already known")

    def _get_or_create_orderitem(oi):
        LOG.info(f"[ galaxus ] orderitem: {oi}")
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            position_item_id=oi.get("LINE_ITEM_ID"),
            defaults={
                "expected_delivery_date": oi.get("DELIVERY_DATE").get(
                    "DELIVERY_START_DATE"
                ),
                "ean": oi["PRODUCT_ID"]["INTERNATIONAL_PID"]["#text"],
                "price": Decimal(oi["PRODUCT_PRICE_FIX"]["PRICE_AMOUNT"]["#text"]),
                "quantity": oi.get("QUANTITY"),
                "sku": oi["PRODUCT_ID"]["SUPPLIER_PID"]["#text"],
                "product_title": oi["PRODUCT_ID"]["DESCRIPTION_SHORT"]["#text"],
            },
        )
        return order_item, created

    order_items = order_data.get("ORDER_ITEM_LIST").get("ORDER_ITEM")

    if isinstance(order_items, list):
        for oi in order_items:
            _get_or_create_orderitem(oi)
    else:
        _get_or_create_orderitem(order_items)


def fetch_orders():
    """Fetch receivable orders from marketplace Mirapodo."""

    # Open a transport
    host, port = M13_GALAXUS_FTP_SERVER, 22
    transport = paramiko.Transport((host, port))

    # Auth
    username, password = M13_GALAXUS_FTP_USER, M13_GALAXUS_FTP_PASSWORD
    transport.connect(None, username, password)

    # Go!
    sftp = paramiko.SFTPClient.from_transport(transport)

    DIRS = [
        "/OrderData/",
        "/OrderData/Live/",
        "/OrderData/Live/dg2partner",
        "/OrderData/Live/partner2dg",
        "/OrderData/Test",
        "/OrderData/Test/dg2partner",
        "/OrderData/Test/partner2dg",
    ]

    resp_str = ""
    for directory in DIRS:
        files = sftp.listdir(directory)

        resp_str += f"\nFILES in dir: {directory}\n"
        resp_str += f"  {files}\n"
        resp_str += "END\n---\n"

    # Close
    if sftp:
        sftp.close()

    if transport:
        transport.close()

    return resp_str
