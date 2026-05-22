import logging

from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from m13.lib.email import send_traceback_as_email
from irisone.services.orders import import_orders

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import orders from irisOne API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            choices=["pending", "opened", "fulfilled"],
            default=None,
            help="Filter orders by status (default: all)",
        )

    @monitor
    def handle(self, *args, **kwargs):
        status = kwargs["status"]
        try:
            counts = import_orders(status=status)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Orders imported: {counts['orders_created']} new, "
                    f"{counts['orders_updated']} updated, "
                    f"{counts['lines_created']} lines created"
                )
            )
        except Exception as exc:
            LOG.exception(exc)
            send_traceback_as_email("M13 irisOne — Order Import failed")
            raise exc

        return 0
