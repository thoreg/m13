import pytest

from core.models import Job
from m13.lib.common import monitor


@pytest.mark.django_db
def test_monitor():
    @monitor
    def successful_function():
        return 0

    @monitor
    def failed_function():
        return -1

    @monitor
    def failed_function_with_exception():
        raise Exception("something went wrong here")

    Job.objects.all().delete()

    successful_function()

    job = Job.objects.get()
    assert job.start is not None
    assert job.end is not None
    assert job.successful is True

    Job.objects.all().delete()

    failed_function()

    job = Job.objects.get()
    assert job.start is not None
    assert job.end is not None
    assert job.successful is False
    assert job.error_msg == "Exception('Unexpected return code -1')"

    Job.objects.all().delete()

    failed_function_with_exception()

    job = Job.objects.get()
    assert job.start is not None
    assert job.end is not None
    assert job.successful is False
    assert job.error_msg == "Exception('something went wrong here')"
