"""Library for common tasks."""
from django.utils import timezone

from core.models import Job


def chunk(lst, chunk_size):
    """Walk through list in chunks."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]  # noqa


def monitor(func):
    def wrapper(*args, **kwargs):
        job = Job.objects.create(
            cmd=func.__module__,
            start=timezone.now(),
        )

        try:
            return_code = func(*args, **kwargs)
            if return_code != 0:
                raise Exception(f"Unexpected return code {return_code}")

            job.successful = True

        except Exception as exc:
            job.error_msg = repr(exc)
            job.successful = False

        job.end = timezone.now()
        job.save()

    return wrapper
