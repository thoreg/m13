import inspect

from core.models import Error


def error(logger, msg):
    """Create error entry."""
    logger.error(msg)

    func = inspect.currentframe().f_back.f_code
    message = "%s: %s in %s:%i" % (
        msg,
        func.co_name,
        func.co_filename,
        func.co_firstlineno,
    )
    Error.objects.create(msg=message)
