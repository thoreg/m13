"""Management command to verify the shop is running and it looks like expected."""

import logging

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand

from m13.lib.common import monitor

LOG = logging.getLogger(__name__)

M13_URL = "https://www.manufaktur13.de/shop/"
LOGO_URL = "https://www.manufaktur13.de/wp-content/uploads/2017/08/navicon.png"

ALLOWED_STARTER = [
    "?add_to_wishlist",
    "?add-to-cart",
]

M13_SHOP = "https://www.manufaktur13.de"

WHITE_LIST = [
    None,
    "#",
    "#0",
    "https://www.youtube.com/c/Manufaktur13De/videos",
    "https://www.facebook.com/pages/Manufaktur-13/510954562300442",
    "https://www.pinterest.de/manufaktur130311/",
    "https://www.instagram.com/manufaktur13/",
    "https://www.youtube.com/channel/UCLHKAq7rTPTOcPTGXygkeLg",
    "https://www.panfilm.de",
    "https://linktr.ee/manufaktur13",
    "javascript:void(0);",
    "#slides__0",
    "#slides__1",
    "#slides__2",
    "#slides__3",
    "#slides__4",
    "#slides__5",
    "https://devowl.io/de/wordpress-real-cookie-banner/",
    "#consent-change",
]


class Command(BaseCommand):
    """..."""

    help = "Check if the shop is up and running."

    def suspicious(self, msg):
        """Send out email on threat detection."""
        msg = f'SNEAKY PETE detected - suspicious: "{msg}"'
        print(msg)

        if not settings.FROM_EMAIL_ADDRESS:
            LOG.critical(msg)
        else:
            mail = EmailMessage(
                msg,
                f'Shop Seite sieht nicht aus wie erwartet "{msg}"',
                settings.FROM_EMAIL_ADDRESS,
                settings.OTTO_ORDER_CSV_RECEIVER_LIST,
            )
            number_of_messages = mail.send()
            LOG.info(f"{number_of_messages} send")

        raise Exception(msg)

    @monitor
    def handle(self, *args, **kwargs):
        """..."""
        verbosity = kwargs.get("verbosity")
        if verbosity:
            verbosity = int(verbosity)
            root_logger = logging.getLogger("")
            if verbosity > 1:
                root_logger.setLevel(logging.DEBUG)

        resp = requests.get(M13_URL)
        if resp.status_code != requests.codes.ok:
            msg = "Request status code of the $hop is not 200 "
            msg += f" - it is tada: >> {resp.status_code} << "
            msg += f"resp_content: {resp.content}"
            return self.suspicious(msg)

        soup = BeautifulSoup(resp.text, "html.parser")

        logo = soup.findAll("img", {"class": "site-logo"})
        # One normal + one lazy load
        if len(logo) != 2:
            return self.suspicious("Logo not found")

        if logo[0]["src"] != LOGO_URL:
            return self.suspicious("Logo has not the right URL")

        for link in soup.find_all("a"):
            href = link.get("href")
            if href in WHITE_LIST:
                continue

            elif href.startswith(M13_SHOP):
                continue

            else:
                suspicious = True
                for allowed in ALLOWED_STARTER:
                    if href.startswith(allowed):
                        suspicious = False
                        break

                if suspicious:
                    msg = f"strange href: BEGIN:{href}:END "
                    try:
                        msg += f"parent: {href.parent} "
                    except Exception as e:
                        msg += "appending parent failed "
                        msg += str(e)

                    return self.suspicious(msg)

        LOG.info("All fine")
        return 0
