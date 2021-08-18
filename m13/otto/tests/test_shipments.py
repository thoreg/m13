import csv

import pytest

from otto.services.shipments import handle_uploaded_file

SHIPMENTS_FILE = 'otto/tests/fixtures/Versandadressen.csv'

@pytest.mark.django_db
def test_import_shipments():
    """Fetched orders are parsed and processes (stored)."""
    with open(SHIPMENTS_FILE) as csv_file:
        handle_uploaded_file(csv_file)
