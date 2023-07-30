"""Prepare feed for upload to Galeria

- Download from M13 shop
- Pimp prices
- Save in BM

Run for dry mode:

    python manage.py m13_galeria_feed_update --dry=1

"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.utils import timezone

from galeria.services.feed import (
    download_feed,
    pimp_prices,
    save_original_feed,
    save_pimped_feed_infos,
)
from m13.lib.common import monitor

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """Prepare product feed for Galeria."""

    help = "__doc__"

    # HERE GEHT ES DANN WEITER

    # - feed runterladen
    # - pimpen
    # - speichern

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry",
            type=int,
            nargs="?",  # argument is optional
            help="When dry run, the final feedupload is not done (only validation)",
            default=0,
        )

    @monitor
    def handle(self, *args, **kwargs):
        """Download product feed from shop and transmit it to Z for validation"""
        try:
            csv_content_as_list = download_feed()
            LOG.info(f"Houston we have a csv with {len(csv_content_as_list)} lines")

            orig_feed = save_original_feed(csv_content_as_list)
            pimped_file_name, pimped_file_xlsx_name = pimp_prices(orig_feed.lines)

            save_pimped_feed_infos(
                orig_feed.path_origin_feed,
                pimped_file_name,
                pimped_file_xlsx_name,
            )

        except Exception as exc:
            LOG.exception(exc)
            now = timezone.now().strftime("%Y-%m-%d (%H:%M:%S)")
            mail = EmailMessage(
                f"{now} Galeria Feed Creation FAILED",
                repr(exc),
                settings.FROM_EMAIL_ADDRESS,
                settings.ZALANDO_LOVERS,
            )
            number_of_messages = mail.send()
            LOG.info(f"Error EMail: {number_of_messages} send")
            raise exc

        return 0
