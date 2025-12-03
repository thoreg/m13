import csv
import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.core import management
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .forms import UploadFileForm
from .models import OrderItem, Shipment
from .services.shipments import handle_uploaded_file

LOG = logging.getLogger(__name__)

LOCATION = "otto"


@login_required
def index(request):
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )
    processable_orderitems = OrderItem.objects.filter(
        fulfillment_status="PROCESSABLE"
    )
    order_ids = set()
    for oi in processable_orderitems:
        order_ids.add(oi.order.marketplace_order_number)

    number_of_processable_orders = len(order_ids)

    context = {
        "number_of_processable": number_of_processable_orders,
        "order_items": order_items,
        "location": LOCATION,
    }
    return render(request, "otto/index.html", context)


def _get_delivery_info(name):
    """Return something human readable for delivery information."""
    MAP = {
        # "DELIVERY_FEE_STANDARD": "Hermes HSI",
        # 'DELIVERY_FEE_STANDARD': 'Hermes S',
        # "DELIVERY_FEE_STANDARD": "DHL Paket",
        "DELIVERY_FEE_STANDARD": "DHL Paket (R)",
    }
    return MAP.get(name, name)


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

    orderitems = (
        OrderItem.objects.filter(fulfillment_status="PROCESSABLE")
        .select_related("order__delivery_address")
        .order_by("order__marketplace_order_number")
    )
    print(f"Found {len(orderitems)} orderitems")

    current_order = None
    current_order_id = None
    for oi in orderitems:
        # Append shipping information at the end of an order (after all orderitems)
        if current_order_id and current_order_id != oi.order.marketplace_order_number:
            price = (
                "%0.2f" % current_order.delivery_fee[0]["deliveryFeeAmount"]["amount"]
            )
            price = price.replace(".", ",")
            writer.writerow(
                [
                    current_order.marketplace_order_number,
                    current_order.delivery_address.first_name,
                    current_order.delivery_address.last_name,
                    f"{current_order.delivery_address.street} {current_order.delivery_address.house_number}",
                    current_order.delivery_address.zip_code,
                    current_order.delivery_address.city,
                    _get_country_information(
                        current_order.delivery_address.country_code
                    ),
                    " ",
                    _get_delivery_info(current_order.delivery_fee[0]["name"]),
                    price,
                    1,
                    "Versandposition",
                    f"OTTO {current_order.marketplace_order_id}",
                    "otto@manufaktur13.de",
                    current_order.created.strftime("%d.%m.%y"),
                ]
            )

        price = "%0.2f" % round(oi.price_in_cent / 100, 2)
        price = price.replace(".", ",")

        writer.writerow(
            [
                oi.order.marketplace_order_number,
                oi.order.delivery_address.first_name,
                oi.order.delivery_address.last_name,
                f"{oi.order.delivery_address.street} {oi.order.delivery_address.house_number}",
                oi.order.delivery_address.zip_code,
                oi.order.delivery_address.city,
                _get_country_information(oi.order.delivery_address.country_code),
                oi.sku,
                oi.product_title,
                price,
                1,
                "Artikel",
                f"OTTO {oi.order.marketplace_order_id}",
                "otto@manufaktur13.de",
                oi.order.created.strftime("%d.%m.%y"),
            ]
        )

        current_order_id = oi.order.marketplace_order_number
        current_order = deepcopy(oi.order)

    if current_order:
        # extra locke for the last shipping position
        price = "%0.2f" % current_order.delivery_fee[0]["deliveryFeeAmount"]["amount"]
        price = price.replace(".", ",")
        writer.writerow(
            [
                current_order.marketplace_order_number,
                current_order.delivery_address.first_name,
                current_order.delivery_address.last_name,
                f"{current_order.delivery_address.street} {current_order.delivery_address.house_number}",
                current_order.delivery_address.zip_code,
                current_order.delivery_address.city,
                _get_country_information(current_order.delivery_address.country_code),
                " ",
                _get_delivery_info(current_order.delivery_fee[0]["name"]),
                price,
                1,
                "Versandposition",
                f"OTTO {current_order.marketplace_order_id}",
                "otto@manufaktur13.de",
                current_order.created.strftime("%d.%m.%y"),
            ]
        )

    return response


@login_required
def import_orders(request):
    """Import orders from OTTO via button click"""
    management.call_command("import_orders", status="PROCESSABLE", verbosity=2)
    management.call_command("import_orders", status="SENT", verbosity=2)
    management.call_command("import_orders", status="RETURNED", verbosity=2)

    return index(request)


@login_required
def upload_tracking_codes(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect(reverse("otto_upload_tracking_codes_success"))
    else:
        form = UploadFileForm()
    return render(
        request,
        "otto/upload_tracking_codes.html",
        {
            "form": form,
            "location": LOCATION,
        },
    )


@login_required
def upload_tracking_codes_success(request):
    shipments = Shipment.objects.all().order_by("-created")[:100]
    return render(
        request,
        "otto/upload_tracking_codes_success.html",
        {
            "shipments": shipments,
            "location": LOCATION,
        },
    )
