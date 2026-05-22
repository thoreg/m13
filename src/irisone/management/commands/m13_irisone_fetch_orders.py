import logging

from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from m13.lib.email import send_traceback_as_email
from irisone.services.orders import import_orders

LOG = logging.getLogger(__name__)

ALL_STATUSES = ["pending", "opened", "fulfilled"]


class Command(BaseCommand):
    help = (
        "Fetch orders from irisOne API for all statuses (pending, opened, fulfilled)."
    )

    @monitor
    def handle(self, *args, **kwargs):
        total = {"orders_created": 0, "orders_updated": 0, "lines_created": 0}

        try:
            for status in ALL_STATUSES:
                self.stdout.write(f"Fetching status={status} ...")
                counts = import_orders(status=status)
                self.stdout.write(
                    f"  {status}: {counts['orders_created']} new, "
                    f"{counts['orders_updated']} updated, "
                    f"{counts['lines_created']} lines"
                )
                for key in total:
                    total[key] += counts[key]

        except Exception as exc:
            LOG.exception(exc)
            send_traceback_as_email("M13 irisOne — Fetch Orders failed")
            raise exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — total: {total['orders_created']} new orders, "
                f"{total['orders_updated']} updated, "
                f"{total['lines_created']} lines created"
            )
        )
        return 0
