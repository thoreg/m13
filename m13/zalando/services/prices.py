import logging
from decimal import Decimal

from zalando.models import PriceTool

LOG = logging.getLogger(__name__)


def update_z_factor(z_factor):
    LOG.info('update_prices_called')
    LOG.info(f'Houston we got price factor: {z_factor}')
    LOG.info(type(z_factor))

    LOG.info(z_factor * Decimal(2))
    LOG.info(z_factor * Decimal(19.95))

    number_of_updated_prices = PriceTool.objects.all().update(active=False)
    LOG.info(f'{number_of_updated_prices} prices updated')

    price_tool, _created = PriceTool.objects.get_or_create(z_factor=z_factor)
    price_tool.active = True
    price_tool.save()

    LOG.info(f'{z_factor} set to ongoing')
