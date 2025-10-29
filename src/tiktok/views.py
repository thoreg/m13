import csv
import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .forms import UploadFileForm
from .models import Order, OrderItem, Shipment
from .services.orders import OrderService
from .services.shipments import handle_uploaded_file

LOG = logging.getLogger(__name__)

DELIVERY_INFO = "DHL Paket"
LOCATION = "tiktok"


@login_required
def index(request) -> HttpResponse:
    """Render TikTok index page."""
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__create_time")
        .select_related("order__delivery_address")[:100]
    )
    number_of_awaiting_shipment = OrderItem.objects.filter(
        status=OrderItem.Status.AWAITING_SHIPMENT
    ).count()

    context = {
        "number_of_awaiting_shipment": number_of_awaiting_shipment,
        "order_items": order_items,
        "location": LOCATION,
    }

    return render(request, "tiktok/index.html", context)


def authcode(request) -> HttpResponse:
    """..."""
    for k, v in request.GET.items():
        LOG.info(f"{k}: {v}")
    context = {
        "location": LOCATION,
    }
    return render(request, "tiktok/index.html", context)


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
        OrderItem.objects.filter(status=OrderItem.Status.AWAITING_SHIPMENT)
        .select_related("order__delivery_address")
        .order_by("order__tiktok_order_id")
    )
    print(f"Found {len(orderitems)} orderitems")

    current_order = None
    current_order_id = None
    for oi in orderitems:
        # Append shipping information at the end of an order (after all orderitems)
        if current_order_id and current_order_id != oi.order.tiktok_order_id:
            price = str(current_order.delivery_fee).replace(".", ",")
            writer.writerow(
                [
                    f"TT{current_order.tiktok_order_id}",
                    current_order.delivery_address.first_name,
                    current_order.delivery_address.last_name,
                    current_order.delivery_address.full_address,
                    current_order.delivery_address.zip_code,
                    current_order.delivery_address.city,
                    _get_country_information(
                        current_order.delivery_address.country_code
                    ),
                    " ",
                    "DHL Paket (R)",
                    price,
                    1,
                    "Versandposition",
                    f"TT{current_order.tiktok_order_id}",
                    current_order.buyer_email,
                    current_order.create_time.strftime("%d.%m.%y"),
                ]
            )

        price = str(oi.price).replace(".", ",")
        writer.writerow(
            [
                f"TT{oi.order.tiktok_order_id}",
                oi.order.delivery_address.first_name,
                oi.order.delivery_address.last_name,
                oi.order.delivery_address.full_address,
                oi.order.delivery_address.zip_code,
                oi.order.delivery_address.city,
                _get_country_information(oi.order.delivery_address.country_code),
                oi.sku,
                oi.tiktok_product_name,
                price,
                1,
                "Artikel",
                f"TT{oi.order.tiktok_order_id}",
                oi.order.buyer_email,
                oi.order.create_time.strftime("%d.%m.%y"),
            ]
        )

        current_order_id = oi.order.tiktok_order_id
        current_order = deepcopy(oi.order)

    if current_order:
        # extra locke for the last shipping position
        price = str(current_order.delivery_fee).replace(".", ",")
        writer.writerow(
            [
                f"TT{current_order.tiktok_order_id}",
                current_order.delivery_address.first_name,
                current_order.delivery_address.last_name,
                current_order.delivery_address.full_address,
                current_order.delivery_address.zip_code,
                current_order.delivery_address.city,
                _get_country_information(current_order.delivery_address.country_code),
                " ",
                "DHL Paket (R)",
                price,
                1,
                "Versandposition",
                f"TT{current_order.tiktok_order_id}",
                current_order.buyer_email,
                current_order.create_time.strftime("%d.%m.%y"),
            ]
        )

    return response


@login_required
def import_orders(request):
    """Import orders from TikTok via button click"""
    order_service = OrderService()
    order_status_list = [choice[0] for choice in Order.Status.choices]

    for order_status in order_status_list:
        order_service.get_orders(Order.Status(order_status))

    return index(request)


@login_required
def upload_tracking_codes(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect(reverse("tiktok_upload_tracking_codes_success"))
    else:
        form = UploadFileForm()
    return render(
        request,
        "tiktok/upload_tracking_codes.html",
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
        "tiktok/upload_tracking_codes_success.html",
        {
            "shipments": shipments,
            "location": LOCATION,
        },
    )
