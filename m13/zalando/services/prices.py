import logging
from decimal import Decimal

from zalando.models import PriceTool

LOG = logging.getLogger(__name__)


def update_z_factor(z_factor):
    number_of_updated_prices = PriceTool.objects.all().update(active=False)
    LOG.info(f'{number_of_updated_prices} prices updated')

    price_tool, _created = PriceTool.objects.get_or_create(z_factor=z_factor)
    price_tool.active = True
    price_tool.save()

    LOG.info(f'{z_factor} set to ongoing')
