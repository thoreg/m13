import csv
import os
import tempfile
from unittest.mock import patch

import pytest
from django.core.management import call_command

from core.models import Category, Error, Price
from m13.lib.csv_reader import read_csv
from zalando.models import PriceTool
from zalando.services.feed import ZalandoException, generate_pp_feed, pimp_prices


@pytest.mark.django_db
def test_pimp_prices():
    """Pimp original stock n price feed."""
    # Cleanup
    Price.objects.all().delete()
    #
    # Prepare two products - one price gets overwritten, one not
    #
    c1 = Category.objects.create(name="test_category_1")
    Price.objects.create(
        sku="CORJACKET-BO-M",
        category=c1,
        costs_production="14.99",
        vk_zalando="24.99",
        vk_otto="25.99",
        pimped_zalando=True,
        ean="0781491971740",
    )
    Price.objects.create(
        sku="CORJACKET-BO-S",
        category=c1,
        costs_production="14.99",
        vk_zalando="24.99",
        vk_otto="25.99",
        pimped_zalando=False,
        ean="0781491971733",
    )

    with open("zalando/tests/data/original_stock_price_feed.csv", "r") as f:
        cr = csv.reader(f.read().splitlines(), delimiter=";")
        lines = list(cr)

    #
    # No Price Factor defined
    #
    with pytest.raises(ZalandoException) as exc_info:
        pimp_prices(lines)
    assert "No price factor found" in str(exc_info.value)

    error = Error.objects.get()
    assert error.cleared is False
    assert error.comment is None
    assert error.msg.startswith("No price factor found: pimp_prices in ")

    pt = PriceTool.objects.create(z_factor=1.3, active=True)
    pt.save()

    # Basic price factor defined but no lines available (FEED not available)
    with pytest.raises(ZalandoException) as exc_info:
        assert pimp_prices(None)
    assert "No feed found" in str(exc_info.value)

    result_file = pimp_prices(lines)
    result_lines = []
    for row in read_csv(result_file):
        result_lines.append(row)

    #
    # Product which has pimped flag set to true gets not auto-pimped - vk_zalando is used instead
    #
    assert result_lines == [
        {
            "article_color": "Schwarz",
            "article_number": "BFShirt-XS-BO",
            "article_size": "XS",
            "ean": "0781491975489",
            "price": "44.95",
            "product_name": "Boyfriend T-Shirt (Black Out) - XS",
            "product_number": "BFShirt-XS-BO",
            "quantity": "10",
            "retail_price": "44.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Grün",
            "article_number": "CORJACKET-SAG-XS",
            "article_size": "XS",
            "ean": "0781491971771",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Sage) - XS",
            "product_number": "CORJACKET-SAG-XS",
            "quantity": "0",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Grün",
            "article_number": "CORJACKET-SAG-S",
            "article_size": "S",
            "ean": "0781491971788",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Sage) - S",
            "product_number": "CORJACKET-SAG-S",
            "quantity": "2",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Grün",
            "article_number": "CORJACKET-SAG-M",
            "article_size": "M",
            "ean": "0781491971795",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Sage) - M",
            "product_number": "CORJACKET-SAG-M",
            "quantity": "4",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Grün",
            "article_number": "CORJACKET-SAG-L",
            "article_size": "L",
            "ean": "0781491971801",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Sage) - L",
            "product_number": "CORJACKET-SAG-L",
            "quantity": "2",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Grün",
            "article_number": "CORJACKET-SAG-XL",
            "article_size": "XL",
            "ean": "0781491971818",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Sage) - XL",
            "product_number": "CORJACKET-SAG-XL",
            "quantity": "2",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Schwarz",
            "article_number": "CORJACKET-BO-XS",
            "article_size": "XS",
            "ean": "0781491971726",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Black Out) - XS",
            "product_number": "CORJACKET-BO-XS",
            "quantity": "3",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Schwarz",
            "article_number": "CORJACKET-BO-XL",
            "article_size": "XL",
            "ean": "0781491971764",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Black Out) - XL",
            "product_number": "CORJACKET-BO-XL",
            "quantity": "3",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Schwarz",
            "article_number": "CORJACKET-BO-S",
            "article_size": "S",
            "ean": "0781491971733",
            "price": "69.95",
            "product_name": "Oversized Cord Jacke (Black Out) - S",
            "product_number": "CORJACKET-BO-S",
            "quantity": "2",
            "retail_price": "69.95",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
        {
            "article_color": "Schwarz",
            "article_number": "CORJACKET-BO-M",
            "article_size": "M",
            "ean": "0781491971740",
            "price": "24.99",
            "product_name": "Oversized Cord Jacke (Black Out) - M",
            "product_number": "CORJACKET-BO-M",
            "quantity": "0",
            "retail_price": "24.99",
            "store": "001",
            "store_article_location": "Manufaktur13 - Chop Shop",
        },
    ]


def test_generate_pp_feed(tmp_path):
    """PP feed gets 4 extra columns derived from the pimped feed."""
    # Pimped feed column order (resolved_row):
    # store(0) ean(1) price(2) retail_price(3) quantity(4)
    # product_number(5) product_name(6) article_number(7)
    # article_color(8) article_size(9) store_article_location(10)
    pimped_csv = tmp_path / "pimped.csv"
    rows = [
        ["store", "ean", "price", "retail_price", "quantity",
         "product_number", "product_name", "article_number",
         "article_color", "article_size", "store_article_location"],
        ["001", "0781491975489", "44.95", "44.95", "10",
         "BFShirt-XS-BO", "Boyfriend T-Shirt - XS", "BFShirt-XS-BO",
         "Schwarz", "XS", "Manufaktur13 - Chop Shop"],
        ["001", "0781491971771", "69.95", "69.95", "0",
         "CORJACKET-SAG-XS", "Oversized Cord Jacke - XS", "CORJACKET-SAG-XS",
         "Grün", "XS", ""],
    ]
    with open(pimped_csv, "w", encoding="UTF8") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)

    pp_file_name = generate_pp_feed(str(pimped_csv))

    assert "import_full_" in os.path.basename(pp_file_name)

    with open(pp_file_name, "r", encoding="UTF8") as f:
        reader = csv.reader(f, delimiter=";")
        result = list(reader)

    assert len(result) == 3  # header + 2 data rows

    header = result[0]
    assert len(header) == 15
    assert header[11] == "erp_ean"
    assert header[12] == "erp_article_number"
    assert header[13] == "erp_store_article_location"
    assert header[14] == "classification"

    # First data row
    row1 = result[1]
    assert row1[11] == row1[1]   # erp_ean == ean
    assert row1[12] == row1[7]   # erp_article_number == article_number
    assert row1[13] == row1[10]  # erp_store_article_location == store_article_location
    assert row1[14] == "default"

    # Second row — store_article_location is empty string
    row2 = result[2]
    assert row2[11] == row2[1]
    assert row2[12] == row2[7]
    assert row2[13] == ""
    assert row2[14] == "default"


@pytest.mark.django_db
@patch("zalando.services.feed.upload_pimped_feed")
# @patch("zalando.services.feed.validate_feed", return_value=200)
@patch("zalando.services.feed.generate_pp_feed", return_value="bogus_pp_file_name")
@patch("zalando.services.feed.pimp_prices", return_value="bogus_file_name")
@patch("zalando.services.feed.download_feed", return_value=[[1, 2, 3, 4, 5, 6]])
def test_m13_zalando_feed_update(
    # mock_download_feed, mock_pimp_prices, mock_validate_feed, mock_upload_pimped_feed
    mock_download_feed,
    mock_pimp_prices,
    mock_generate_pp_feed,
    mock_upload_pimped_feed,
):
    """Methods for feed upload are available and called."""
    call_command("m13_zalando_feed_update", dry="1", verbosity=2)
    mock_download_feed.assert_called_once()
    mock_pimp_prices.assert_called_once()
    mock_generate_pp_feed.assert_called_once()
    # mock_validate_feed.assert_called_once()
    mock_upload_pimped_feed.assert_not_called()

    mock_download_feed.reset_mock()
    mock_pimp_prices.reset_mock()
    mock_generate_pp_feed.reset_mock()
    # mock_validate_feed.reset_mock()
    mock_upload_pimped_feed.reset_mock()

    call_command("m13_zalando_feed_update", verbosity=2)
    mock_download_feed.assert_called_once()
    mock_pimp_prices.assert_called_once()
    mock_generate_pp_feed.assert_called_once()
    # mock_validate_feed.assert_called_once()
    mock_upload_pimped_feed.assert_called_once()
