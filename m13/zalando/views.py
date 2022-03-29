import csv
import datetime as dt
import json
import logging
from datetime import date, datetime, timedelta
from pprint import pformat, pprint
from secrets import compare_digest

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.transaction import atomic, non_atomic_requests
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from zalando.services.prices import update_z_factor

from .forms import PriceToolForm
from .models import FeedUpload, OEAWebhookMessage, OrderItem, PriceTool, Product, StatsOrderItems

LOG = logging.getLogger(__name__)


@login_required
def price_feed(request):
    """Price Feed Index View."""
    feed_uploads = FeedUpload.objects.all().order_by('-created')[:5]

    if request.method == 'POST':
        form = PriceToolForm(request.POST)
        if form.is_valid():
            update_z_factor(form.cleaned_data['z_factor'])
            return HttpResponseRedirect(reverse('zalando_index'))
    else:
        form = PriceToolForm()

    try:
        price_tool = PriceTool.objects.get(active=True)
        z_factor = price_tool.z_factor
    except PriceTool.DoesNotExist:
        z_factor = 'UNDEFINED'

    ctx = {
        'feed_uploads': feed_uploads,
        'form': form,
        'z_factor': z_factor,
    }
    return render(request, 'zalando/price_feed.html', ctx)


@login_required
def index(request):
    """Zalando Index View."""
    order_items = (
        OrderItem.objects.all()
        .order_by('-order__order_date')
        .select_related('order__delivery_address')[:100]
    )
    products = {p['ean']: p['title'] for p in Product.objects.all().values()}
    ctx = {
        'dbyesterday': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        'yesterday': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'today': datetime.now().strftime('%Y-%m-%d'),
        'order_items': order_items,
        'products': products,
    }
    LOG.info(ctx)
    return render(request, 'zalando/index.html', ctx)


@csrf_exempt
@require_POST
@non_atomic_requests
def oea_webhook(request):
    """Handle incoming webhook messages."""
    if not settings.ZALANDO_OEM_WEBHOOK_TOKEN:
        return HttpResponse('Token not defined.', content_type='text/plain')

    given_token = request.headers.get('x-api-key', '')
    if not compare_digest(given_token, settings.ZALANDO_OEM_WEBHOOK_TOKEN):
        return HttpResponseForbidden(
            'Incorrect token in header',
            content_type='text/plain'
        )

    OEAWebhookMessage.objects.filter(
        created__lte=timezone.now() - dt.timedelta(days=365)
    ).delete()

    try:
        payload = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        LOG.exception('JSON decode failed')
        LOG.error(request.body)
        return HttpResponse(
            'Request body is not JSON', content_type='text/plain')

    OEAWebhookMessage.objects.create(payload=payload)
    process_oea_webhook_payload(payload)
    return HttpResponse('Message received okay.', content_type='text/plain')


@atomic
def process_oea_webhook_payload(payload):
    LOG.info(payload)


@login_required
def orderitems_csv(request, day):
    """Return all processible orderitems as csv."""

    LOG.info(request.__dict__)
    LOG.info(f'GET: {request.GET.__dict__}')
    LOG.info(f'day: {day}')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{date}.csv"'},
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

    # orderitems = (OrderItem.objects
    #                        .filter(fulfillment_status='PROCESSABLE')
    #                        .select_related('order__delivery_address')
    #                        .order_by('order__marketplace_order_number'))
    # print(f'Found {len(orderitems)} orderitems')

    # current_order = None
    # current_order_id = None
    # for oi in orderitems:

    #     # Append shipping information at the end of an order (after all orderitems)
    #     if current_order_id and current_order_id != oi.order.marketplace_order_number:
    #         price = '%0.2f' % current_order.delivery_fee[0]['deliveryFeeAmount']['amount']
    #         price = price.replace('.', ',')
    #         writer.writerow([
    #             current_order.marketplace_order_number,
    #             current_order.delivery_address.first_name,
    #             current_order.delivery_address.last_name,
    #             f'{current_order.delivery_address.street} {current_order.delivery_address.house_number}',
    #             current_order.delivery_address.zip_code,
    #             current_order.delivery_address.city,
    #             _get_country_information(current_order.delivery_address.country_code),
    #             ' ',
    #             _get_delivery_info(current_order.delivery_fee[0]['name']),
    #             price,
    #             1,
    #             'Versandposition',
    #             f'OTTO {current_order.marketplace_order_id}',
    #             'otto@manufaktur13.de'
    #         ])

    #     price = '%0.2f' % round(oi.price_in_cent / 100, 2)
    #     price = price.replace('.', ',')

    #     writer.writerow([
    #         oi.order.marketplace_order_number,
    #         oi.order.delivery_address.first_name,
    #         oi.order.delivery_address.last_name,
    #         f'{oi.order.delivery_address.street} {oi.order.delivery_address.house_number}',
    #         oi.order.delivery_address.zip_code,
    #         oi.order.delivery_address.city,
    #         _get_country_information(oi.order.delivery_address.country_code),
    #         oi.sku,
    #         oi.product_title,
    #         price,
    #         1,
    #         'Artikel',
    #         f'OTTO {oi.order.marketplace_order_id}',
    #         'otto@manufaktur13.de'
    #     ])

    #     current_order_id = oi.order.marketplace_order_number
    #     current_order = deepcopy(oi.order)

    # if current_order:
    #     # extra locke for the last shipping position
    #     price = '%0.2f' % current_order.delivery_fee[0]['deliveryFeeAmount']['amount']
    #     price = price.replace('.', ',')
    #     writer.writerow([
    #         current_order.marketplace_order_number,
    #         current_order.delivery_address.first_name,
    #         current_order.delivery_address.last_name,
    #         f'{current_order.delivery_address.street} {current_order.delivery_address.house_number}',
    #         current_order.delivery_address.zip_code,
    #         current_order.delivery_address.city,
    #         _get_country_information(current_order.delivery_address.country_code),
    #         ' ',
    #         _get_delivery_info(current_order.delivery_fee[0]['name']),
    #         price,
    #         1,
    #         'Versandposition',
    #         f'OTTO {current_order.marketplace_order_id}',
    #         'otto@manufaktur13.de'
    #     ])

    # email = request.GET.get('email')
    # if email:
    #     LOG.info('Houston we got to send an email')
    #     if not settings.FROM_EMAIL_ADDRESS:
    #         LOG.error('settings.FROM_EMAIL_ADDRESS needs to be defined')
    #         return response

    #     if not settings.OTTO_ORDER_CSV_RECEIVER_LIST:
    #         LOG.error('settings.OTTO_ORDER_CSV_RECEIVER_LIST needs to be defined')
    #         return response

    #     LOG.info(f'settings.FROM_EMAIL_ADDRESS: {settings.FROM_EMAIL_ADDRESS}')
    #     LOG.info(f'settings.OTTO_ORDER_CSV_RECEIVER_LIST: {settings.OTTO_ORDER_CSV_RECEIVER_LIST}')

    #     message = EmailMessage(
    #         f'OTTO Bestellungen - {now.strftime("%Y/%m/%d")}',
    #         'OTTO Bestellungen als csv - Frohes Schaffen!!',
    #         settings.FROM_EMAIL_ADDRESS,
    #         settings.OTTO_ORDER_CSV_RECEIVER_LIST,
    #     )
    #     message.attach(
    #         f'{now.strftime("%Y/%m/%d")}_otto_bestellungen.csv',
    #         response.getvalue(),
    #         'text/csv')
    #     number_of_messages = message.send()
    #     LOG.info(f'{number_of_messages} send')

    return response


@login_required
def stats_orderitems(request):
    return JsonResponse(
        list(StatsOrderItems.objects.all().values()), safe=False)
