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

    with pytest.raises(Exception) as exc_info:
        failed_function()
    # these asserts are identical; you can use either one
    assert exc_info.value.args[0] == "Unexpected return code -1"
    assert str(exc_info.value) == "Unexpected return code -1"

    job = Job.objects.get()
    assert job.start is not None
    assert job.end is None
    assert job.successful is False

    Job.objects.all().delete()

    with pytest.raises(Exception) as exc_info:
        failed_function_with_exception()
    # these asserts are identical; you can use either one
    assert exc_info.value.args[0] == "something went wrong here"
    assert str(exc_info.value) == "something went wrong here"

    job = Job.objects.get()
    assert job.start is not None
    assert job.end is None
    assert job.successful is False
