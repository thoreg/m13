import sys
import traceback

from django.conf import settings
from django.core.mail import send_mail


def send_traceback_as_email(subject, message=None):
    """Send out traceback of given exception as email."""
    msg = traceback.format_exc(*sys.exc_info())  # type: ignore
    if message:
        msg += f"\n\n{message}\n\n"
    send_mail(
        subject,
        msg,
        settings.FROM_EMAIL_ADDRESS,
        settings.ADMINS,
        fail_silently=False)
