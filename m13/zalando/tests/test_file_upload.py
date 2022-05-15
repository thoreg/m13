from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from zalando.models import TransactionFileUpload


def test_multi_file_upload(client, django_user_model, django_db_setup):
    """Multi File Upload is present and works properly."""
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    upload_url = reverse('zalando_finance_upload_files')

    response = client.get(upload_url)
    assert response.status_code == 200

    files = []
    for idx in range(1, 4):
        fp = open(f'zalando/tests/fixtures/daily_sales_report_{idx}.csv', 'rb')
        files.append(fp)

    response = client.post(upload_url, {
        'month': 202203,
        'original_csv': files
    })

    entries = TransactionFileUpload.objects.all()
    assert len(entries) == 3

    for idx in range(1, 4):
        entry = entries[idx - 1]
        assert entry.original_csv.name.endswith(f'daily_sales_report_{idx}.csv')
        assert entry.month == 202203
        assert entry.status_code_upload is True
        assert entry.status_code_processing is False
