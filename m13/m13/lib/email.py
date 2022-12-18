import sys
import traceback

from django.conf import settings
from django.core.mail import send_mail


def send_traceback_as_email(subject, message=None):
    """Send out traceback of given exception as email."""
    msg = ""
    if message:
        msg += f"\n\n{message}\n\n"

    _exc_type, _exc_value, exc_traceback = sys.exc_info()

    msg += "\n*** format_exc, first and last line:\n"
    formatted_lines = traceback.format_exc().splitlines()
    msg += formatted_lines[0]
    msg += formatted_lines[-1]

    msg += "\n*** format_tb:\n"
    msg += repr(traceback.format_tb(exc_traceback))
    msg += f"*** tb_lineno: {exc_traceback.tb_lineno}"

    send_mail(
        subject,
        msg,
        settings.FROM_EMAIL_ADDRESS,
        settings.ADMINS[0][1],
        fail_silently=False,
    )
