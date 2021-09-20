from datetime import datetime, timezone


def now_as_str():
    """Return now() as human readable string."""
    now = datetime.now()
    return now.strftime('%Y-%m-%dT%H_%M_%S')


def time_str2object(time_str):
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(
        tzinfo=timezone.utc)
