"""Esty views.

OAuth Information:
https://developers.etsy.com/documentation/essentials/authentication/#proof-key-for-code-exchange-pkce

"""

import csv
import logging
import os
from copy import deepcopy

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .common import get_auth_token
from .forms import UploadFileForm
from .models import AuthGrant, AuthToken, Order, OrderItem, Shipment, StatsOrderItems
from .services.orders import get_receipts, process_receipts
from .services.shipments import handle_uploaded_file

LOG = logging.getLogger(__name__)

M13_ETSY_API_KEY = os.getenv("M13_ETSY_API_KEY")
M13_ETSY_GET_AUTH_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
M13_ETSY_OAUTH_REDIRECT = os.getenv("M13_ETSY_OAUTH_REDIRECT")
M13_ETSY_SHOP_ID = os.getenv("M13_ETSY_SHOP_ID")

DELIVERY_FEE_STANDARD = "DHL Paket"


def _render_auth_request_not_found(request):
    ctx = {
        "error": "AuthRequest2.DoesNotExist",
        "error_descrption": "No AuthRequest2 found",
    }
    return render(request, "etsy/oauth_error.html", ctx)


@login_required
def orders(request):
    """Display orders from etsy."""
    token = get_auth_token()
    if not token:
        return _render_auth_request_not_found(request)

    response = get_receipts(token)
    process_receipts(response)

    return redirect(reverse("etsy_index"))


@login_required
def orderitems_csv(request):
    """Return all processible orderitems as csv."""

    def __get_street_offset(city):
        """Return end index of the street depending on how many words of the city."""
        return -2 - len(city.split())

    now = timezone.now()
    now_as_str = now.strftime("%Y-%m-%dT%H_%M_%S")
    file_name = f"{now_as_str}_etsy.csv"
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
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
        OrderItem.objects.filter(fulfillment_status="PAID")
        .select_related("order__delivery_address")
        .order_by("order__marketplace_order_id")
    )
    print(f"Found {len(orderitems)} orderitems")

    current_order = None
    current_order_id = None
    for oi in orderitems:
        # Append shipping information at the end of an order (after all orderitems)
        if current_order_id and current_order_id != oi.order.marketplace_order_id:
            amount = current_order.delivery_fee["amount"]
            divisor = current_order.delivery_fee["divisor"]
            price = "%0.2f" % (int(amount) / int(divisor))
            price = price.replace(".", ",")

            first_name, last_name, street = (
                current_order.delivery_address.get_address_as_columns()
            )
            zip_code = current_order.delivery_address.zip_code
            city = current_order.delivery_address.city
            country = current_order.delivery_address.country_code

            writer.writerow(
                [
                    f"ETSY{current_order.marketplace_order_id}",
                    first_name,
                    last_name,
                    street,
                    zip_code,
                    city,
                    country,
                    " ",
                    DELIVERY_FEE_STANDARD,
                    price,
                    1,
                    "Versandposition",
                    f"ETSY{current_order.marketplace_order_id}",
                    current_order.delivery_address.buyer_email,
                    current_order.created.strftime("%d.%m.%y"),
                ]
            )

        price = "%0.2f" % round(oi.price_in_cent / 100, 2)
        price = price.replace(".", ",")

        first_name, last_name, street = (
            oi.order.delivery_address.get_address_as_columns()
        )
        zip_code = oi.order.delivery_address.zip_code
        city = oi.order.delivery_address.city
        country = oi.order.delivery_address.country_code

        writer.writerow(
            [
                f"ETSY{oi.order.marketplace_order_id}",
                first_name,
                last_name,
                street,
                zip_code,
                city,
                country,
                oi.sku,
                oi.product_title,
                price,
                oi.quantity,
                "Artikel",
                f"ETSY{oi.order.marketplace_order_id}",
                oi.order.delivery_address.buyer_email,
                oi.order.created.strftime("%d.%m.%y"),
            ]
        )

        current_order_id = oi.order.marketplace_order_id
        current_order = deepcopy(oi.order)

    if current_order:
        amount = current_order.delivery_fee["amount"]
        divisor = current_order.delivery_fee["divisor"]
        price = "%0.2f" % (int(amount) / int(divisor))
        price = price.replace(".", ",")

        first_name, last_name, street = (
            current_order.delivery_address.get_address_as_columns()
        )
        zip_code = current_order.delivery_address.zip_code
        city = current_order.delivery_address.city
        country = current_order.delivery_address.country_code

        writer.writerow(
            [
                f"ETSY{current_order.marketplace_order_id}",
                first_name,
                last_name,
                street,
                zip_code,
                city,
                country,
                " ",
                DELIVERY_FEE_STANDARD,
                price,
                1,
                "Versandposition",
                f"ETSY{current_order.marketplace_order_id}",
                current_order.delivery_address.buyer_email,
                current_order.created.strftime("%d.%m.%y"),
            ]
        )

    return response


def oauth(request):
    """OAuth redirect url."""
    error = request.GET.get("error")
    if error:
        error_description = request.GET.get("error_description")
        ctx = {"error": error, "error_descrption": error_description}
        return render(request, "etsy/oauth_error.html", ctx)
    else:
        auth_code = request.GET.get("code")
        state = request.GET.get("state")
        try:
            auth_request = AuthGrant.objects.get(
                state=state,
            )
        except AuthGrant.DoesNotExist:
            return _render_auth_request_not_found(request)

        # Verify functionality - qqq
        req_body = {
            "client_id": M13_ETSY_API_KEY,
            "code_verifier": auth_request.verifier.encode("utf8"),
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": M13_ETSY_OAUTH_REDIRECT,
        }
        LOG.debug(f"POST: req_body {req_body}")
        resp = requests.post(M13_ETSY_GET_AUTH_TOKEN_URL, data=req_body)
        resp_json = resp.json()
        LOG.debug("- POST RESPONSE ---------------------------------------")
        LOG.debug(resp_json)
        LOG.debug("- POST RESPONSE ----------------------------------- END")

        AuthToken.objects.create(
            token=resp_json.get("access_token"),
            refresh_token=resp_json.get("refresh_token"),
        )

        context = {"msg": "Hooray we have an AUTH_TOKEN"}
        return render(request, "etsy/oauth_success.html", context)


@login_required
def index(request):
    """Index view of the etsy app."""
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )

    ctx = {
        "number_of_paid": OrderItem.objects.filter(fulfillment_status="PAID").count(),
        "number_of_orders": Order.objects.count(),
        "number_of_orderitems": OrderItem.objects.count(),
        "order_items": order_items,
    }
    return render(request, "etsy/index.html", ctx)


@login_required
def shipments(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect(reverse("etsy_upload_tracking_codes_success"))
    else:
        form = UploadFileForm()
    return render(request, "etsy/upload_tracking_codes.html", {"form": form})


@login_required
def upload_tracking_codes_success(request):
    shipments = Shipment.objects.all().order_by("-created")[:100]
    return render(
        request, "etsy/upload_tracking_codes_success.html", {"shipments": shipments}
    )


@login_required
def stats_orderitems(request):
    return JsonResponse(list(StatsOrderItems.objects.all().values()), safe=False)
