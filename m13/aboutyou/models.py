from django.db import models
from django_extensions.db.models import TimeStampedModel


class BatchRequest(TimeStampedModel):
    """Track batch requests (e.g. stock updates)."""

    id = models.CharField(primary_key=True)
    started = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, null=True)
    completed = models.DateTimeField(null=True)


class Address(TimeStampedModel):
    """We get from otto only shipping and billing addresses.

    No customer id - no email
    """

    addition = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    first_name = models.CharField(max_length=128)
    house_number = models.CharField(max_length=16)
    last_name = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    title = models.CharField(max_length=32, null=True, blank=True)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64, unique=True)
    order_date = models.DateTimeField()

    invoice_address = models.ForeignKey(
        Address, related_name="invoice_address_set", null=True, on_delete=models.PROTECT
    )
    delivery_address = models.ForeignKey(
        Address, related_name="delivery_address_set", on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        OPEN = "open"
        SHIPPED = "shipped"
        CANCELED = "cancelled"
        RETURNED = "returned"
        MIXED = "mixed"

    status = models.CharField(
        max_length=11,
        choices=Status.choices,
        default=Status.OPEN,
    )


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    fulfillment_status = models.CharField(max_length=32)

    price_in_cent = models.PositiveIntegerField()

    position_item_id = models.CharField(max_length=36)
    sku = models.CharField(max_length=36)
    vat_rate = models.PositiveSmallIntegerField()

    # returned_date = models.DateTimeField(null=True, blank=True)
    # sent_date = models.DateTimeField(null=True, blank=True)

    # carrier = models.CharField(max_length=32, null=True, blank=True)
    # carrier_service_code = models.CharField(max_length=128, null=True, blank=True)
    # tracking_number = models.CharField(max_length=128, null=True, blank=True)

    def __repr__(self) -> str:
        return (
            f"({self.order}:{self.order.order_date}) sku: {self.sku} "
            f"price: {self.price_in_cent} "
            f"fulfillment_status: {self.fulfillment_status}"
        )


class Shipment(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    carrier = models.CharField(max_length=128)
    tracking_info = models.CharField(max_length=256)
    response_status_code = models.PositiveSmallIntegerField()
    response = models.JSONField()


# {'items': [{'billing_additional': None,
#             'billing_city': 'West Anthony',
#             'billing_country_code': 'IT',
#             'billing_recipient_first_name': 'Victoria',
#             'billing_recipient_gender': 'f',
#             'billing_recipient_last_name': 'Wright',
#             'billing_street': '485 Sean Freeway Suite 477',
#             'billing_zip_code': '62037',
#             'carrier_key': 'UB_Post_FI',
#             'cost_with_tax': 4590,
#             'cost_without_tax': 3717,
#             'created_at': '2025-04-22T14:20:27.476Z',
#             'currency_code': 'EUR',
#             'custom_data': None,
#             'customer_key': '3e140d4e-6737-4fb3-b3a1-c69f375944a7',
#             'delivery_document_url': '/api/v1/orders/sb_100000000039/delivery_document',
#             'order_items': [{'custom_data': None,
#                              'id': 5119,
#                              'price_with_tax': 2295,
#                              'price_without_tax': 1858,
#                              'product_variant': 13647,
#                              'return_tracking_key': '',
#                              'shipment_tracking_key': '',
#                              'sku': 'FB-16',
#                              'status': 'open',
#                              'vat': 19.0},
#                             {'custom_data': None,
#                              'id': 5120,
#                              'price_with_tax': 2295,
#                              'price_without_tax': 1858,
#                              'product_variant': 13651,
#                              'return_tracking_key': '',
#                              'shipment_tracking_key': '',
#                              'sku': 'FB-18',
#                              'status': 'open',
#                              'vat': 19.0}],
#             'order_number': 'sb_100000000039',
#             'payment_method': None,
#             'shipping_additional': 'mind',
#             'shipping_city': 'East Kirsten',
#             'shipping_collection_point_customer_key': None,
#             'shipping_collection_point_description': None,
#             'shipping_collection_point_key': None,
#             'shipping_collection_point_type': None,
#             'shipping_country_code': 'SG',
#             'shipping_recipient_first_name': 'David',
#             'shipping_recipient_gender': 'f',
#             'shipping_recipient_last_name': 'Edwards',
#             'shipping_street': '6482 Vazquez Curve Apt. 423',
#             'shipping_zip_code': '82586',
#             'shop': 1,
#             'shopify_order_id': None,
#             'status': 'open',
#             'updated_at': '2025-04-22T14:20:29.697Z'},
