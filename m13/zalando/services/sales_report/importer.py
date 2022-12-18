"""Zalando sales/return reports processing code lives here.

Reports from Zalando about sales and returns are stored in Dropbox from where
they are grabbed for further processing.

"""

import os
import tempfile
import zipfile
from datetime import datetime, timezone

import dropbox
from django.utils import timezone as django_utils_timezone

from m13.lib.csv_reader import read_csv
from m13.lib.django.managers import BulkCreateManager
from zalando.models import SalesReport, SalesReportImport

AUTH_TOKEN = os.getenv("M13_DROPBOX_AUTH_TOKEN")
REPORTS_PATH = os.getenv("M13_DROPBOX_ZALANDO_REPORTS_PATH")

EXTRACT_DIR = "/tmp"


class DownloadFailed(Exception):
    pass


def import_sales_reports(month):
    """Return CSV file which contains the requested report."""
    if not all([AUTH_TOKEN, REPORTS_PATH]):
        print("\nERROR - env variables AUTH_TOKEN and REPORTS_PATH needed\n")
        return []

    print("Starting to connect to Dropbox")
    dbx = dropbox.Dropbox(AUTH_TOKEN)
    print(f"Start checking files for month {month}")
    for file_path in _get_files_from_dropbox(dbx, month):
        _download_and_extract_file(dbx, file_path)

    for file in os.listdir(EXTRACT_DIR):
        path = f"{EXTRACT_DIR}/{file}"
        print(f"Import {path}")
        _import_sales_report(path, month)


def _get_files_from_dropbox(dbx, month):
    """Return list of available files (full path)."""
    result = []

    path = f"{REPORTS_PATH}/{month}"
    print(f"Checking path {path}")
    for entry in dbx.files_list_folder(path).entries:
        print(f"Found {entry.name}")
        result.append(f"{path}/{entry.name}")

    return result


def _download_and_extract_file(dbx, path):
    """Return content of requested file."""
    print(f"Download {path}")
    metadata, f = dbx.files_download(path)

    if metadata.name.endswith("PDF"):
        print(f"Skipping PDF file {metadata.name}")
        return

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(f.content)
        temp.seek(0)
        with zipfile.ZipFile(temp, "r") as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)


def __as_float(value):
    """Return float from string."""
    return float(value.replace(",", "."))


def __as_datetime_with_tz(datetime_string, dt_format="%d.%m.%Y"):
    """Return parsed datetime object salted with timezone information."""
    return datetime.strptime(datetime_string, dt_format).replace(tzinfo=timezone.utc)


def _import_sales_report(path, month):
    """..."""
    if not path.endswith(".CSV"):
        print(f"Path does not end with CSV - path: {path}")
        return

    month = int(month.replace("/", ""))
    sri, created = SalesReportImport.objects.get_or_create(name=path, month=month)
    if not created:
        print(f"Looks like {path} for {month} is already known dude")
        return

    bulk_mgr = BulkCreateManager(chunk_size=20)

    for row in read_csv(path):

        try:
            # This field seems not to be fixed
            partner_provision = row["PROVISION_PARTNER"]
        except KeyError:
            partner_provision = row["E_PROVISION_PARTNER"]

        bulk_mgr.add(
            SalesReport(
                year=int(row["ACCOUNTING_YEAR"]),
                month=int(row["ACCOUNTING_MONTH"]),
                created_date=__as_datetime_with_tz(row["CREATED_DATE"]),
                currency=row["CURRENCY"],
                order_number=row["ORDER_NUMBER"],
                ean=row["EAN"],
                shipping_return_date=__as_datetime_with_tz(
                    row["PARTNER_SHIPPING_DATE/PARTNER_RETURN_DATE"]
                ),
                order_date=__as_datetime_with_tz(row["ORDER_DATE"]),
                partner_units=int(row["PARTNER_UNITS"]),
                partner_revenue=__as_float(row["PARTNER_REVENUE"]),
                partner_provision=__as_float(partner_provision),
                import_reference=sri,
            )
        )

    bulk_mgr.done()
    sri.processed = django_utils_timezone.now()
    sri.save()
