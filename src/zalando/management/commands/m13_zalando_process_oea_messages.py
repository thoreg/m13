from django.core.management.base import BaseCommand

from zalando.services.orders import process_new_oea_records


class Command(BaseCommand):
    help = "Process unprocessed OEA (Order Events API) webhook messages."

    def handle(self, *args, **options):
        process_new_oea_records()
