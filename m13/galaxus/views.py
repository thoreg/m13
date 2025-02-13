import csv
import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from .models import OrderItem
from .services.orders import fetch_orders

LOG = logging.getLogger(__name__)

LOCATION = "galaxus"


@login_required
def index(request):
    """Mirapodo index page."""
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )

    context = {
        "order_items": order_items,
        "location": LOCATION,
    }
    return render(request, "galaxus/index.html", context)


def _get_country_information(country_code):
    """..."""
    MAP = {
        "AUT": "Österreich",
        "CHE": "Schweiz",
        "DEU": "Deutschland",
    }
    return MAP.get(country_code, country_code)


@login_required
def orderitems_csv(request):
    """Return all processible orderitems as csv."""
    now = timezone.now()
    now_as_str = now.strftime("%Y-%m-%dT%H_%M_%S")
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{now_as_str}.csv"'},
    )

    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response, delimiter=";")
    writer.writerow(
        [
            "Bestellnummer",
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
        ]
    )

    #    .filter(internal_status='IMPORTED')
    orderitems = (
        OrderItem.objects.filter(order__internal_status="IMPORTED")
        .select_related("order__delivery_address")
        .order_by("order__marketplace_order_id")
    )
    print(f"Found {len(orderitems)} orderitems")

    current_order = None
    current_order_id = None
    for oi in orderitems:
        # Append shipping information at the end of an order (after all orderitems)
        if current_order_id and current_order_id != oi.order.marketplace_order_id:
            writer.writerow(
                [
                    current_order.marketplace_order_id,
                    current_order.delivery_address.first_name,
                    current_order.delivery_address.last_name,
                    f"{current_order.delivery_address.street} {current_order.delivery_address.house_number}",
                    current_order.delivery_address.zip_code,
                    current_order.delivery_address.city,
                    _get_country_information(
                        current_order.delivery_address.country_code
                    ),
                    " ",
                    oi.order.delivery_fee,
                    0,
                    1,
                    "Versandposition",
                    f"MIRAPODO {current_order.marketplace_order_id}",
                    current_order.mail,
                    current_order.created.strftime("%d.%m.%y"),
                ]
            )

        writer.writerow(
            [
                oi.order.marketplace_order_id,
                oi.order.delivery_address.first_name,
                oi.order.delivery_address.last_name,
                f"{oi.order.delivery_address.street} {oi.order.delivery_address.house_number}",
                oi.order.delivery_address.zip_code,
                oi.order.delivery_address.city,
                _get_country_information(oi.order.delivery_address.country_code),
                oi.sku,
                oi.billing_text,
                str(oi.item_price).replace(".", ","),
                1,
                "Artikel",
                f"MIRAPODO {oi.order.marketplace_order_id}",
                oi.order.mail,
                oi.order.created.strftime("%d.%m.%y"),
            ]
        )

        current_order_id = oi.order.marketplace_order_id
        current_order = deepcopy(oi.order)

    if current_order:
        # extra locke for the last shipping position
        writer.writerow(
            [
                current_order.marketplace_order_id,
                current_order.delivery_address.first_name,
                current_order.delivery_address.last_name,
                f"{current_order.delivery_address.street} {current_order.delivery_address.house_number}",
                current_order.delivery_address.zip_code,
                current_order.delivery_address.city,
                _get_country_information(current_order.delivery_address.country_code),
                " ",
                oi.order.delivery_fee,
                0,
                1,
                "Versandposition",
                f"MIRAPODO {current_order.marketplace_order_id}",
                current_order.mail,
                current_order.created.strftime("%d.%m.%y"),
            ]
        )

    return response


@login_required
def import_orders(request):
    """Import orders from Mirapodo via button click"""
    resp_str = fetch_orders()
    # return index(request)
    return render(
        request,
        "galaxus/resp_str.html",
        {
            "resp_str": resp_str,
            "location": LOCATION,
        }
    )
