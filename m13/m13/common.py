import base64
import time
from datetime import datetime, timezone


def now_as_str():
    """Return now() as human readable string."""
    now = datetime.now()
    return now.strftime('%Y-%m-%dT%H_%M_%S')


def time_str2object(time_str):
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
        tzinfo=timezone.utc)


def timestamp_from_epoch(epoch):
    """Return timestamp which is recognized by psql."""
    return time.strftime('%Y-%m-%d %H:%M:%SZ', time.localtime(epoch))


# https://gist.github.com/cameronmaske/f520903ade824e4c30ab
def base64_encode(string):
    """
    Removes any `=` used as padding from the encoded string.
    """
    encoded = base64.urlsafe_b64encode(string)
    return encoded.rstrip(b'=')


def base64_decode(string):
    """
    Adds back in the required padding before decoding.
    """
    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    return base64.urlsafe_b64decode(string)
