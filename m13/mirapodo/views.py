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

from .models import OrderItem
from .services.orders import fetch_orders

LOG = logging.getLogger(__name__)


@login_required
def index(request):
    """Mirapodo index page."""
    order_items = (
        OrderItem.objects.all()
        .order_by('-order__order_date')
        .select_related('order__delivery_address')[:100]
    )
    # number_of_processable = OrderItem.objects.filter(
    #     fulfillment_status='PROCESSABLE').count()

    context = {
        # 'number_of_processable': number_of_processable,
        'order_items': order_items
    }
    return render(request, 'mirapodo/index.html', context)


def _get_delivery_info(name):
    """Return something human readable for delivery information."""
    MAP = {
        'DELIVERY_FEE_STANDARD': 'Hermes HSI',
        # 'DELIVERY_FEE_STANDARD': 'Hermes S',
        # 'DELIVERY_FEE_STANDARD': 'DHL Paket',
    }
    return MAP.get(name, name)


def _get_country_information(country_code):
    """..."""
    MAP = {
        'AUT': 'Österreich',
        'CHE': 'Schweiz',
        'DEU': 'Deutschland',

    }
    return MAP.get(country_code, country_code)


@login_required
def orderitems_csv(request):
    """Return all processible orderitems as csv."""
    now = datetime.now()
    now_as_str = now.strftime('%Y-%m-%dT%H_%M_%S')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{now_as_str}.csv"'},
    )

    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Bestellnummer',
        'Vorname',
        'Name',
        'Straße',
        'PLZ',
        'Ort',
        'Land',
        'Artikelnummer',
        'Artikelname',
        'Preis (Brutto)',
        'Menge',
        'Positionstyp',
        'Anmerkung',
        'EMAIL'
    ])

    orderitems = (OrderItem.objects
                           .filter(fulfillment_status='PROCESSABLE')
                           .select_related('order__delivery_address')
                           .order_by('order__marketplace_order_number'))
    print(f'Found {len(orderitems)} orderitems')

    current_order = None
    current_order_id = None
    for oi in orderitems:

        # Append shipping information at the end of an order (after all orderitems)
        if current_order_id and current_order_id != oi.order.marketplace_order_number:
            price = '%0.2f' % current_order.delivery_fee[0]['deliveryFeeAmount']['amount']
            price = price.replace('.', ',')
            writer.writerow([
                current_order.marketplace_order_number,
                current_order.delivery_address.first_name,
                current_order.delivery_address.last_name,
                f'{current_order.delivery_address.street} {current_order.delivery_address.house_number}',
                current_order.delivery_address.zip_code,
                current_order.delivery_address.city,
                _get_country_information(current_order.delivery_address.country_code),
                ' ',
                _get_delivery_info(current_order.delivery_fee[0]['name']),
                price,
                1,
                'Versandposition',
                f'OTTO {current_order.marketplace_order_id}',
                'otto@manufaktur13.de'
            ])

        price = '%0.2f' % round(oi.price_in_cent / 100, 2)
        price = price.replace('.', ',')

        writer.writerow([
            oi.order.marketplace_order_number,
            oi.order.delivery_address.first_name,
            oi.order.delivery_address.last_name,
            f'{oi.order.delivery_address.street} {oi.order.delivery_address.house_number}',
            oi.order.delivery_address.zip_code,
            oi.order.delivery_address.city,
            _get_country_information(oi.order.delivery_address.country_code),
            oi.sku,
            oi.product_title,
            price,
            1,
            'Artikel',
            f'OTTO {oi.order.marketplace_order_id}',
            'otto@manufaktur13.de'
        ])

        current_order_id = oi.order.marketplace_order_number
        current_order = deepcopy(oi.order)

    if current_order:
        # extra locke for the last shipping position
        price = '%0.2f' % current_order.delivery_fee[0]['deliveryFeeAmount']['amount']
        price = price.replace('.', ',')
        writer.writerow([
            current_order.marketplace_order_number,
            current_order.delivery_address.first_name,
            current_order.delivery_address.last_name,
            f'{current_order.delivery_address.street} {current_order.delivery_address.house_number}',
            current_order.delivery_address.zip_code,
            current_order.delivery_address.city,
            _get_country_information(current_order.delivery_address.country_code),
            ' ',
            _get_delivery_info(current_order.delivery_fee[0]['name']),
            price,
            1,
            'Versandposition',
            f'OTTO {current_order.marketplace_order_id}',
            'otto@manufaktur13.de'
        ])

    return response


@login_required
def import_orders(request):
    """Import orders from Mirapodo via button click"""
    fetch_orders()
    return index(request)
