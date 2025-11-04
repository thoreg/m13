"""Gather information about the used system, e.g. free disk space."""

import shutil

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **kwargs):
        msg = ""
        total, used, free = shutil.disk_usage("/")

        msg += "Total: %d GiB\n" % (total // (2**30))
        msg += "Used: %d GiB\n" % (used // (2**30))
        msg += "Free: %d GiB\n" % (free // (2**30))

        used_in_percent = round(used * 100 / total, 2)

        msg += f"Used in percent: {used_in_percent}\n"

        mail = EmailMessage(
            f"M13 - BM - Disk Usage {used_in_percent}",
            msg,
            settings.FROM_EMAIL_ADDRESS,
            settings.ADMINS,
        )
        number_of_messages = mail.send()
        print(f"{number_of_messages} send")
