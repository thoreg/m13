"""Handle feed upload from M13 shop to zalando retailer API endpoint.

Download, transform, validate and upload feed

Run for dry mode:

    python manage.py m13_zalando_feed_update --dry=1

"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.utils import timezone

from m13.lib.common import monitor
from zalando.services.feed import (
    download_feed,
    pimp_prices,
    save_original_feed,
    upload_pimped_feed,
    validate_feed,
)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """..."""

    help = "Update product feed at zalando"

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
        dry_run = kwargs.get("dry")
        verbosity = kwargs.get("verbosity")
        if verbosity:
            verbosity = int(verbosity)
            root_logger = logging.getLogger("")
            if verbosity > 1:
                root_logger.setLevel(logging.DEBUG)

        try:
            csv_content_as_list = download_feed()
            LOG.info(f"Houston we have a csv with {len(csv_content_as_list)} lines")

            dto = save_original_feed(csv_content_as_list)
            pimped_file_name = pimp_prices(dto.lines)
            validation_result = validate_feed(pimped_file_name)

            if dry_run:
                LOG.info("Return early because of --dry-run")
                return 0
            else:
                LOG.info("Uploading transformed feed now")

            upload_pimped_feed(
                pimped_file_name,
                200,
                dto,
                validation_result,
            )

        except Exception as exc:
            LOG.exception(exc)
            now = timezone.now().strftime("%Y-%m-%d (%H:%M:%S)")
            mail = EmailMessage(
                f"{now} Zalando Feed Upload FAILED",
                repr(exc),
                settings.FROM_EMAIL_ADDRESS,
                settings.ZALANDO_LOVERS,
            )
            number_of_messages = mail.send()
            LOG.info(f"Error EMail: {number_of_messages} send")
            raise exc

        return 0
