"""Library for common tasks."""


def chunk(lst, chunk_size):
    """Walk through list in chunks."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]
