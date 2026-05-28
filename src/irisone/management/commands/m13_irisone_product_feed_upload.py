import logging

from django.core.management.base import BaseCommand

from m13.lib.common import monitor
from m13.lib.email import send_traceback_as_email
from irisone.services.feed import upload_product_feed

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Upload product data feed to irisOne QuickConnect (run every 12h)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            choices=["full", "delta"],
            default="full",
            help="Feed type: full (default) or delta",
        )

    @monitor
    def handle(self, *args, **kwargs):
        feed_type = kwargs["type"]
        try:
            feed_upload = upload_product_feed(feed_type=feed_type)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Product feed uploaded: {feed_upload.number_of_items} items "
                    f"(status {feed_upload.status_code})"
                )
            )
        except Exception as exc:
            LOG.exception(exc)
            send_traceback_as_email("M13 irisOne — Product Feed Upload failed")
            raise exc

        return 0
