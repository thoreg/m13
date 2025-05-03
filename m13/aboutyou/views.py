import csv
import logging
from copy import deepcopy

from django.contrib.auth.decorators import login_required
from django.core import management
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from core.models import Price, Product

from .forms import UploadFileForm
from .models import OrderItem, Shipment
from .services.shipments import handle_uploaded_file

LOG = logging.getLogger(__name__)

DELIVERY_FEE_STANDARD = "DHL Standard National DE"
DELIVERY_FEE_PRICE = "3,95"

LOCATION = "aboutyou"


@login_required
def index(request):
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )
    number_of_processable = OrderItem.objects.filter(fulfillment_status="open").count()

    context = {
        "number_of_processable": number_of_processable,
        "order_items": order_items,
        "location": LOCATION,
    }
    return render(request, "aboutyou/index.html", context)


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

    products = Product.objects.all().values_list("ean", "name")
    products_dict = {entry[0]: entry[1] for entry in products}
    prices = Price.objects.all().values_list("sku", "ean")
    prices_dict = {entry[0]: entry[1] for entry in prices}

    def __get_product_title(sku: str, prices_map: dict, products_map: dict) -> str:
        try:
            ean = prices_map[sku]
        except KeyError:
            LOG.info(f"sku: {sku} not in prices")
            return "sku_not_in_prices"

        try:
            title = products_map[ean]
        except KeyError:
            LOG.info(f"ean: {ean} not in products")
            return "ean_not_in_products"

        return title

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
        OrderItem.objects.filter(fulfillment_status="open")
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
                    current_order.delivery_address.country_code,
                    " ",
                    DELIVERY_FEE_STANDARD,
                    DELIVERY_FEE_PRICE,
                    1,
                    "Versandposition",
                    f"{current_order.marketplace_order_id}",
                    "ay@manufaktur13.de",
                    current_order.created.strftime("%d.%m.%y"),
                ]
            )

        price = "%0.2f" % round(oi.price_in_cent / 100, 2)
        price = price.replace(".", ",")

        writer.writerow(
            [
                oi.order.marketplace_order_id,
                oi.order.delivery_address.first_name,
                oi.order.delivery_address.last_name,
                f"{oi.order.delivery_address.street} {oi.order.delivery_address.house_number}",
                oi.order.delivery_address.zip_code,
                oi.order.delivery_address.city,
                oi.order.delivery_address.country_code,
                oi.sku,
                __get_product_title(oi.sku, prices_dict, products_dict),
                price,
                1,
                "Artikel",
                f"{oi.order.marketplace_order_id}",
                "ay@manufaktur13.de",
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
                current_order.delivery_address.country_code,
                " ",
                DELIVERY_FEE_STANDARD,
                DELIVERY_FEE_PRICE,
                1,
                "Versandposition",
                f"{current_order.marketplace_order_id}",
                "ay@manufaktur13.de",
                current_order.created.strftime("%d.%m.%y"),
            ]
        )

    return response


@login_required
def import_orders(request):
    """Import orders from ABOUTYOU via button click"""
    management.call_command("m13_ay_sync_orders")

    return index(request)


@login_required
def upload_tracking_codes(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect(reverse("ay_upload_tracking_codes_success"))
    else:
        form = UploadFileForm()
    return render(
        request,
        "aboutyou/upload_tracking_codes.html",
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
        "aboutyou/upload_tracking_codes_success.html",
        {
            "shipments": shipments,
            "location": LOCATION,
        },
    )
