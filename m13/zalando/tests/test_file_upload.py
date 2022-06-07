import hashlib

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from zalando.models import DailyShipmentReport, TransactionFileUpload


def test_multi_file_upload(client, django_user_model, django_db_setup):
    """Multi File Upload is present and works properly."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    upload_url = reverse('zalando_finance_upload_files')

    response = client.get(upload_url)
    assert response.status_code == 200

    original_files = []
    original_files_md5sums = []
    for idx in range(3):
        fp = open(f'zalando/tests/fixtures/daily_sales_report_{idx}.csv', 'rb')
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {'original_csv': original_files})

    entries = TransactionFileUpload.objects.all()
    assert len(entries) == 3

    for idx in range(3):
        entry = entries[idx]
        assert entry.original_csv.name.endswith(f'daily_sales_report_{idx}.csv')
        assert entry.processed is False
        assert entry.file_name == f'daily_sales_report_{idx}.csv'

        with open(entry.original_csv.name, 'rb') as result_file:
            content = result_file.read()
            md5_hash = hashlib.md5()
            md5_hash.update(content)
            assert original_files_md5sums[idx] == md5_hash.hexdigest()

    # Multiple uploads of the same files do not lead to multiple storage of objects
    response = client.post(upload_url, {'original_csv': original_files})
    response = client.post(upload_url, {'original_csv': original_files})
    response = client.post(upload_url, {'original_csv': original_files})

    assert TransactionFileUpload.objects.count() == 3
    assert DailyShipmentReport.objects.count() == 12
