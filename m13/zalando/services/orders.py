"""Business logic for orders from Zalando.

Incoming data from OEA - Order Event API from Zalando looks like:

Assigned (order has been assigned to the store):
------------------------------------------------
{'event_id': '215bcb87-7fb2-4cad-8dba-ebde508e71b6',
 'items': [{'article_location': 'Manufaktur13 - Chop Shop',
            'article_number': 'NECKW-NA',
            'currency': 'EUR',
            'ean': '0781491971467',
            'item_id': 'b634ddef-6371-4f6d-b5cf-6f59d3cab09e',
            'price': 24.95,
            'zalando_article_number': 'MGQ54G005-K110ONE000'}],
 'order_id': '478d3ff7-f94a-41f7-8095-c62b3073f9b8',
 'order_number': '10103350851695',
 'state': 'assigned',
 'store_id': '001',
 'timestamp': '2021-09-15T09:09:28.221195Z'}


Fullfilled (order items were picked and completed in the Connected Retail tool.
The order is ready to be shipped to the customer.):
---------------------------------------------------
{
    'customer_billing_address': {
        'address_line_1': 'Am Anger 28 b',
        'city': 'Eichstätt',
        'country_code': 'DE',
        'first_name': 'R.',
        'last_name': 'K.',
        'zip_code': '85072'
    },
    'delivery_details': {
        'delivery_carrier_name': 'DHL_DE',
        'delivery_tracking_number': '00340414644694802419',
        'return_carrier_name': 'DHL_DE',
        'return_tracking_number': '00340414644694802419',
    },
    'event_id': '70947cfd-c3fc-4421-91e5-9e62b10153c3',
    'items': [
        {
            'article_location': 'Manufaktur13 - Chop Shop',
            'article_number': 'NECKW-NA',
            'currency': 'EUR',
            'ean': '0781491971467',
            'item_id': 'b634ddef-6371-4f6d-b5cf-6f59d3cab09e',
            'price': 24.95,
            'zalando_article_number': 'MGQ54G005-K110ONE000'
        }
    ],
    'order_id': '478d3ff7-f94a-41f7-8095-c62b3073f9b8',
    'order_number': '10103350851622',
    'state': 'fulfilled',
    'store_id': '001',
    'timestamp': '2021-09-16T06:21:39.390060Z'
}

"""
import logging

from django.utils import timezone

from zalando.models import Address, OEAWebhookMessage, Order, OrderItem

LOG = logging.getLogger(__name__)


def get_address(address_data):
    """Return Address object for given data.
    {
        'address_line_1': 'Am Anger 12 b',
        'city': 'Eichstädt',
        'country_code': 'DE',
        'first_name': 'R.',
        'last_name': 'K.',
        'zip_code': '85172'
    }
    """
    try:
        address, _ = Address.objects.get_or_create(
            line=address_data['address_line_1'],
            city=address_data['city'],
            country_code=address_data['country_code'],
            first_name=address_data['first_name'],
            last_name=address_data['last_name'],
            zip_code=address_data['zip_code']
        )
    except KeyError:
        LOG.error(f'Something unforseen - address_data: {address_data}')
        return None

    return address


def process_orderitem(order, oi, delivery_infos):
    """Process orderitem from order event api."""
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        position_item_id=oi['item_id'],
        ean=oi['ean'],
        defaults={
            'article_number': oi['article_number'],
            'carrier': delivery_infos['carrier'],
            'currency': oi['currency'],
            'fulfillment_status': order.status,
            'orig_created_timestamp': oi['timestamp'],
            'orig_modified_timestamp': oi['timestamp'],
            'price_in_cent': oi['price'] * 100,
            'tracking_number': delivery_infos['tracking_number'],
        }
    )
    LOG.info(f'   iid: {oi["item_id"]} ean: {order_item.ean} created: {created} creation_datetime: {oi["timestamp"]}')

    if not created:
        order_item.fulfillment_status = order.status
        order_item.orig_modified_timestamp = oi['timestamp']
        order_item.save()


def mark_as_processed(oea_msg_obj):
    """Mark this object as processed."""
    oea_msg_obj.processed = timezone.now()
    oea_msg_obj.save()


def process_new_oea_records():
    """Process all unprocessed oem records."""
    unprocessed = OEAWebhookMessage.objects.filter(processed=None)
    for oea_msg in unprocessed:
        entry = oea_msg.payload
        order, created = Order.objects.get_or_create(
            marketplace_order_id=entry['order_id'],
            store_id=entry['store_id'],
            defaults={
                'marketplace_order_number': entry['order_number'],
                'order_date': entry['timestamp'],
                'created': entry['timestamp'],
                'last_modified_date': entry['timestamp'],
                'status': entry['state']
            })

        if created:
            LOG.info(
                f'order: {order.marketplace_order_id} '
                f'order_number: {order.marketplace_order_number} '
                f'order.id: {order.id} order created'
            )

        else:
            LOG.info(
                f'order: {order.marketplace_order_id} '
                f'order_number: {order.marketplace_order_number} '
                f'order.id: {order.id} order - begin'
            )

            # import ipdb; ipdb.set_trace()
            # if order.last_modified_date > time_str2object(entry['timestamp']):
            #     LOG.info('\t\tooo - continue')
            #     mark_as_processed(oea_msg)
            #     continue

            order.status = entry['state']
            order.last_modified_date = entry['timestamp']

        # We are done here if order status is just 'assigned
        if order.status == 'assigned':
            LOG.info('\t\tfulfillment status is assigned - return early')
            mark_as_processed(oea_msg)
            continue

        dd = entry.get('delivery_details')
        if not dd:
            LOG.error('status is != "assigned" but no delivery infos')
            continue

        for oi in entry['items']:
            oi['timestamp'] = entry['timestamp']
            try:
                process_orderitem(order, oi, {
                    'carrier': dd['delivery_carrier_name'],
                    'tracking_number': dd['delivery_tracking_number']
                })
            except KeyError:
                LOG.error('KeyError in zalando orderitem processing')
                LOG.error(entry)

        address_data = entry.get('customer_billing_address')
        if address_data:
            order.delivery_address = get_address(address_data)
        else:
            LOG.error(f'No address data found but expected entry: {entry}')

        order.save()

        LOG.info(
            f'order: {order.marketplace_order_id} '
            f'order_number: {order.marketplace_order_number} '
            f'order.id: {order.id} order updated - end'
        )

        mark_as_processed(oea_msg)
