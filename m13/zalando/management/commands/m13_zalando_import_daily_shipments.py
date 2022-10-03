from django.core.management.base import BaseCommand

from zalando.services.daily_shipment_reports import import_all_unprocessed_daily_shipment_reports


class Command(BaseCommand):
    help = "Import daily shipment reports."

    def handle(self, *args, **kwargs):
        """..."""
        import_all_unprocessed_daily_shipment_reports()
