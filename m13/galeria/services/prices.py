import logging

from galeria.models import PriceTool

LOG = logging.getLogger(__name__)


def update_g_factor(factor):
    number_of_updated_prices = PriceTool.objects.all().update(active=False)
    LOG.info(f"{number_of_updated_prices} prices updated")

    price_tool, _created = PriceTool.objects.get_or_create(g_factor=factor)
    price_tool.active = True
    price_tool.save()

    LOG.info(f"{factor} set to ongoing")
