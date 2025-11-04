from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from zalando.services.daily_shipment_reports import (
    import_all_unprocessed_daily_shipment_reports,
)


class Command(BaseCommand):
    help = "Import daily shipment reports."

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        import_all_unprocessed_daily_shipment_reports()
        return 0
