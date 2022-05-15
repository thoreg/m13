import csv
from unittest.mock import patch

import pytest
from django.core.management import call_command

from zalando.models import PriceTool
from zalando.services.feed import ZalandoException, pimp_prices


@pytest.mark.django_db
def test_pimp_prices():
    """Pimp original stock n price feed."""
    with open('zalando/tests/data/original_stock_price_feed.csv', 'r') as f:
        cr = csv.reader(f.read().splitlines(), delimiter=';')
        lines = list(cr)

    with pytest.raises(ZalandoException) as exc_info:
        pimp_prices(lines)
    assert 'No price factor found' in str(exc_info.value)

    pt = PriceTool.objects.create(z_factor=2, active=True)
    pt.save()

    # Basic price factor defined and lines are available
    assert pimp_prices(lines) is not None

    # Basic price factor defined but no lines available (FEED not available)
    with pytest.raises(ZalandoException) as exc_info:
        assert pimp_prices(None)
    assert 'No feed found' in str(exc_info.value)


@pytest.mark.django_db
@patch('zalando.services.feed.upload_pimped_feed')
@patch('zalando.services.feed.validate_feed', return_value=200)
@patch('zalando.services.feed.pimp_prices', return_value='bogus_file_name')
@patch('zalando.services.feed.download_feed', return_value=[[1, 2, 3, 4, 5, 6]])
def test_m13_zalando_feed_update(
        mock_download_feed,
        mock_pimp_prices,
        mock_validate_feed,
        mock_upload_pimped_feed):
    """Methods for feed upload are available and called."""
    call_command('m13_zalando_feed_update', dry='1', verbosity=2)
    mock_download_feed.assert_called_once()
    mock_pimp_prices.assert_called_once()
    mock_validate_feed.assert_called_once()
    mock_upload_pimped_feed.assert_not_called()

    mock_download_feed.reset_mock()
    mock_pimp_prices.reset_mock()
    mock_validate_feed.reset_mock()
    mock_upload_pimped_feed.reset_mock()

    call_command('m13_zalando_feed_update', verbosity=2)
    mock_download_feed.assert_called_once()
    mock_pimp_prices.assert_called_once()
    mock_validate_feed.assert_called_once()
    mock_upload_pimped_feed.assert_called_once()
