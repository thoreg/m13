
from .models import PriceTool


def get_z_factor():
    price_tool = PriceTool.objects.get(active=True)
    if not price_tool:
        return 'UNDEFINED'

    return float(price_tool.z_factor)
