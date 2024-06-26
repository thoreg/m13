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
    """The customer address model for Etsy.

    The email can be empty if the customer submits an order as guest.
    The only effect on this is that there will be no shipping confirmation
    email send out.

    """

    buyer_email = models.EmailField(null=True, blank=True)
    buyer_user_id = models.IntegerField()
    city = models.CharField(max_length=128)
    country_code = models.CharField(max_length=32)
    formatted_address = models.CharField(max_length=256)
    zip_code = models.CharField(max_length=32)

    def get_address_as_columns(self) -> tuple[str, str, str, str]:
        """Return single fields for firstname, surname, street"""
        splitted_by_newline = self.formatted_address.split("\n")
        splitted_by_newline = [
            line.strip() for line in splitted_by_newline if len(line.strip()) > 0
        ]
        first_line = splitted_by_newline[0].strip().split()
        first_name = " ".join(first_line[:-1])
        last_name = first_line[-1]

        # Part which holds the street
        street = splitted_by_newline[1].strip()
        additional_info = ""
        if len(splitted_by_newline) >= 5:
            additional_info = splitted_by_newline[2].strip()

        return first_name, last_name, street, additional_info


class Order(TimeStampedModel):
    marketplace_order_id = models.CharField(max_length=64)
    order_date = models.DateTimeField()
    last_modified_date = models.DateTimeField()
    delivery_address = models.ForeignKey(
        Address, related_name="delivery_address_set", on_delete=models.PROTECT
    )

    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        OPEN = "OPEN", "Open"
        PAID = "PAID", "Paid"
        PAYMENT_PROCESSING = "PAYMENT_PROCESSING", "Payment Processing"
        CANCELED = "CANCELED"
        PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially Refunded"

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

    quantity = models.PositiveSmallIntegerField(default=1)


class Shipment(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    carrier = models.CharField(max_length=128)
    tracking_info = models.CharField(max_length=256)
    response_status_code = models.PositiveSmallIntegerField()
    response = models.JSONField()


class StatsOrderItems(models.Model):
    month = models.DateTimeField()
    status = models.CharField(max_length=16)
    count = models.IntegerField()
    revenue = models.FloatField()

    class Meta:
        managed = False
        db_table = "etsy_orderitem_stats"
