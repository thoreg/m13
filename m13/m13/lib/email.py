import sys
import traceback

from django.conf import settings
from django.core.mail import send_mail


def send_traceback_as_email(subject, message=None):
    """Send out traceback of given exception as email."""
    msg = ''
    if message:
        msg += f"\n\n{message}\n\n"

    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg += "\n*** print_tb:\n"
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    msg += "*** print_exception:"
    # exc_type below is ignored on 3.5 and later
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
    msg += "\n*** print_exc:\n"
    traceback.print_exc(limit=2, file=sys.stdout)
    msg += "\n*** format_exc, first and last line:\n"
    formatted_lines = traceback.format_exc().splitlines()
    msg += formatted_lines[0]
    msg += formatted_lines[-1]

    msg += "\n*** extract_tb:\n"
    msg += repr(traceback.extract_tb(exc_traceback))
    msg += "\n*** format_tb:\n"
    msg += repr(traceback.format_tb(exc_traceback))
    msg += f"*** tb_lineno: {exc_traceback.tb_lineno}"

    send_mail(
        subject,
        msg,
        settings.FROM_EMAIL_ADDRESS,
        settings.ADMINS,
        fail_silently=False)
