from django.db import models
from django_extensions.db.models import TimeStampedModel


class AuthGrant(TimeStampedModel):
    verifier = models.CharField(max_length=512)
    code_challenge = models.CharField(max_length=256)
    state = models.CharField(max_length=8)


class AuthToken(TimeStampedModel):
    token = models.CharField(max_length=128)
    refresh_token = models.CharField(max_length=128)


class Address(TimeStampedModel):
    """We get from otto only shipping and billing addresses.

    No customer id - no email
    """
    buyer_email = models.EmailField()
    buyer_user_id = models.IntegerField()
    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    formatted_address = models.CharField(max_length=256)
    zip_code = models.CharField(max_length=32)


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    marketplace_order_number = models.CharField(max_length=32)
    order_date = models.DateTimeField()
    last_modified_date = models.DateTimeField()
    delivery_address = models.ForeignKey(
        Address,
        related_name="delivery_address_set",
        on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        OPEN = 'OPEN', 'Open'
        PAID = 'PAID', 'Paid'
        PAYMENT_PROCESSING = 'PAYMENT_PROCESSING', 'Payment Processing'

    status = models.CharField(
        max_length=18,
        choices=Status.choices,
        default=Status.OPEN,
    )

    delivery_fee = models.JSONField()


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateTimeField()
    fulfillment_status = models.CharField(max_length=32)

    price_in_cent = models.PositiveIntegerField()
    currency = models.CharField(max_length=8)

    position_item_id = models.CharField(max_length=36)
    ean = models.CharField(max_length=16)
    product_title = models.CharField(max_length=256)
    sku = models.CharField(max_length=36)

    carrier = models.CharField(max_length=32, null=True, blank=True)
    tracking_number = models.CharField(max_length=128, null=True, blank=True)
