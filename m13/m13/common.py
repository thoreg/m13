from datetime import datetime


def now_as_str():
    """Return now() as human readable string."""
    now = datetime.now()
    return now.strftime('%Y-%m-%dT%H_%M_%S')
