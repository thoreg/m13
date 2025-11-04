import hashlib
from decimal import Decimal

from django.urls import reverse

from core.models import MarketplaceConfig
from core.services import article_stats
from zalando.models import SalesReport, SalesReportFileUpload

NUMBER_OF_FIXTURE_FILES = 4


def test_multi_file_upload(client, django_user_model, django_db_setup):
    """Multi File Upload is present and works properly."""
    MarketplaceConfig.objects.create(
        name=article_stats.Marketplace.ZALANDO,
        shipping_costs=Decimal("3.55"),
        return_costs=Decimal("3.55"),
        provision_in_percent=None,
        vat_in_percent=19,
        generic_costs_in_percent=3,
    )

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    upload_url = reverse("zalando_finance_upload_files")

    response = client.get(upload_url)
    assert response.status_code == 200

    original_files = []
    original_files_md5sums = []
    for idx in range(NUMBER_OF_FIXTURE_FILES):
        fp = open(f"zalando/tests/fixtures/monthly_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    entries = SalesReportFileUpload.objects.all()
    assert len(entries) == NUMBER_OF_FIXTURE_FILES

    for idx in range(NUMBER_OF_FIXTURE_FILES):
        entry = entries[idx]
        assert entry.original_csv.name.endswith(f"monthly_sales_report_{idx}.csv")
        assert entry.processed is True
        assert entry.file_name == f"monthly_sales_report_{idx}.csv"

        with open(entry.original_csv.name, "rb") as result_file:
            content = result_file.read()
            md5_hash = hashlib.md5()
            md5_hash.update(content)
            assert original_files_md5sums[idx] == md5_hash.hexdigest()

    # Multiple uploads of the same files do not lead to multiple storage of objects
    response = client.post(upload_url, {"original_csv": original_files})
    response = client.post(upload_url, {"original_csv": original_files})
    response = client.post(upload_url, {"original_csv": original_files})

    assert SalesReportFileUpload.objects.count() == NUMBER_OF_FIXTURE_FILES
    assert SalesReport.objects.count() == 16


def test_zalando_shipment_stats_file_upload(client, django_user_model, django_db_setup):
    """The right marketplace configuration is taken on file upload."""
    SalesReportFileUpload.objects.all().delete()
    SalesReport.objects.all().delete()
    #
    # 0 - First upload of files - reference to the current marketplace configuration
    #
    config1 = MarketplaceConfig.objects.create(
        name=article_stats.Marketplace.ZALANDO,
        shipping_costs=Decimal("3.55"),
        return_costs=Decimal("3.55"),
        provision_in_percent=None,
        vat_in_percent=19,
        generic_costs_in_percent=3,
    )

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    upload_url = reverse("zalando_finance_upload_files")

    response = client.get(upload_url)
    assert response.status_code == 200

    original_files = []
    original_files_md5sums = []
    for idx in [0, 1]:
        fp = open(f"zalando/tests/fixtures/monthly_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    #
    # 1 - Second upload of files - reference to the current marketplace configuration
    #
    config2 = MarketplaceConfig.objects.create(
        name=article_stats.Marketplace.ZALANDO,
        shipping_costs=Decimal("2.55"),
        return_costs=Decimal("2.55"),
        provision_in_percent=None,
        vat_in_percent=7,
        generic_costs_in_percent=5,
    )
    original_files = []
    original_files_md5sums = []
    for idx in [2, 3]:
        fp = open(f"zalando/tests/fixtures/monthly_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    all_sales_report_entries = SalesReport.objects.all()
    assert all_sales_report_entries.count() == 16
    assert (
        all_sales_report_entries.filter(zalando_marketplace_config=config1).count() == 8
    )
    assert (
        all_sales_report_entries.filter(zalando_marketplace_config=config2).count() == 8
    )
