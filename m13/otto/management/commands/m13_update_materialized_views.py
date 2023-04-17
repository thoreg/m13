import logging

from django.core.management.base import BaseCommand
from django.db import connection

LOG = logging.getLogger(__name__)

MATERIALIZED_VIEWS = [
    "etsy_orderitem_stats",
    "otto_orderitem_stats",
    "zalando_orderitem_stats",
]


class Command(BaseCommand):
    help = "Simple management command to update existing materialized views."

    def handle(self, *args, **kwargs):
        for view in MATERIALIZED_VIEWS:
            with connection.cursor() as cursor:
                self.stdout.write(self.style.SUCCESS(f"Update {view}"))
                cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")

        return 0
