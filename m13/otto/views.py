import csv
import logging
from copy import deepcopy
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import management
from django.core.mail import EmailMessage
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from m13.lib.psql import dictfetchall

from .forms import UploadFileForm
from .models import OrderItem, Shipment, StatsOrderItems
from .services.shipments import handle_uploaded_file

LOG = logging.getLogger(__name__)


@login_required
def index(request):
    order_items = (
        OrderItem.objects.all()
        .order_by("-order__order_date")
        .select_related("order__delivery_address")[:100]
    )
    number_of_processable = OrderItem.objects.filter(
        fulfillment_status="PROCESSABLE"
    ).count()

    context = {
        "number_of_processable": number_of_processable,
        "order_items": order_items,
    }
    return render(request, "otto/index.html", context)


def _get_delivery_info(name):
    """Return something human readable for delivery information."""
    MAP = {
        "DELIVERY_FEE_STANDARD": "Hermes HSI",
        # 'DELIVERY_FEE_STANDARD': 'Hermes S',
        # 'DELIVERY_FEE_STANDARD': 'DHL Paket',
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
    now = datetime.now()
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
            ]
        )

    email = request.GET.get("email")
    if email:
        LOG.info("Houston we got to send an email")
        if not settings.FROM_EMAIL_ADDRESS:
            LOG.error("settings.FROM_EMAIL_ADDRESS needs to be defined")
            return response

        if not settings.OTTO_ORDER_CSV_RECEIVER_LIST:
            LOG.error("settings.OTTO_ORDER_CSV_RECEIVER_LIST needs to be defined")
            return response

        LOG.info(f"settings.FROM_EMAIL_ADDRESS: {settings.FROM_EMAIL_ADDRESS}")
        LOG.info(
            f"settings.OTTO_ORDER_CSV_RECEIVER_LIST: {settings.OTTO_ORDER_CSV_RECEIVER_LIST}"
        )

        message = EmailMessage(
            f'OTTO Bestellungen - {now.strftime("%Y/%m/%d")}',
            "OTTO Bestellungen als csv - Frohes Schaffen!!",
            settings.FROM_EMAIL_ADDRESS,
            settings.OTTO_ORDER_CSV_RECEIVER_LIST,
        )
        message.attach(
            f'{now.strftime("%Y/%m/%d")}_otto_bestellungen.csv',
            response.getvalue(),
            "text/csv",
        )
        number_of_messages = message.send()
        LOG.info(f"{number_of_messages} send")

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
    return render(request, "otto/upload_tracking_codes.html", {"form": form})


@login_required
def upload_tracking_codes_success(request):
    shipments = Shipment.objects.all().order_by("-created")[:100]
    return render(
        request, "otto/upload_tracking_codes_success.html", {"shipments": shipments}
    )


@login_required
def stats(request):
    ctx = {"status_per_month": {}}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                DATE_TRUNC('month', modified) AS month,
                fulfillment_status AS status,
                COUNT(id) AS count,
                SUM(price_in_cent)::float/100 AS umsatz
            FROM
                otto_orderitem
            GROUP BY
                month,
                fulfillment_status
            ORDER BY
                month DESC
        """
        )
        result = dictfetchall(cursor)
        for entry in result:
            month = entry["month"].strftime("%Y%m")
            status = entry["status"]
            if month not in ctx["status_per_month"]:
                ctx["status_per_month"][month] = {}
            ctx["status_per_month"][month][status] = entry

        number_orderitems_all = OrderItem.objects.all().count()
        number_orderitems_return = OrderItem.objects.filter(
            fulfillment_status="RETURNED"
        ).count()
        return_quote = 100 * number_orderitems_return / number_orderitems_all
        ctx["total"] = {
            "number_orderitems_all": number_orderitems_all,
            "number_orderitems_return": number_orderitems_return,
            "return_quote": return_quote,
        }

    sales_revenue_by_status = []
    for month, status_values in ctx["status_per_month"].items():
        row = [month]
        for status in ["PROCESSABLE", "SENT", "RETURNED"]:
            values = status_values.get(status)
            if values:
                row.extend([status, values["count"], values["umsatz"]])
            else:
                row.extend([status, "-", "-"])

        sales_revenue_by_status.append(row)

    ctx["sales_revenue_by_status"] = sales_revenue_by_status
    return render(request, "otto/stats.html", {"ctx": ctx})


@login_required
def stats_orderitems(request):
    return JsonResponse(list(StatsOrderItems.objects.all().values()), safe=False)
