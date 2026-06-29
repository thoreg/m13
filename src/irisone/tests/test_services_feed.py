"""Tests for irisone.services.feed._build_irisone_csv and _build_irisone_product_csv.

Pricing now follows the same rules as the Zalando pimped feed:
factor pricing (PriceTool.z_factor + shipping fee, rounded to an allowed
price), the pimped_zalando hard overwrite, hardcoded price_overwrites,
SKU_BLACKLIST filtering and out-of-season duplication.
"""

import csv

import pytest

from core.models import Price
from irisone.services.feed import _build_irisone_csv, _build_irisone_product_csv
from zalando.models import PriceTool


def _write_shop_csv(path, rows):
    with open(path, "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)


def _read_csv(path):
    with open(path, "r", encoding="UTF-8") as f:
        return list(csv.reader(f, delimiter=";"))


def _shop_rows(path, rows):
    _write_shop_csv(path, rows)
    return list(
        csv.reader(path.read_text(encoding="UTF-8").splitlines(), delimiter=";")
    )


@pytest.fixture
def active_factor(db):
    """Active price factor of 1.0 so factor pricing is easy to reason about."""
    return PriceTool.objects.create(z_factor=1.0, active=True)


# --- stock feed ---


@pytest.mark.django_db
def test_build_irisone_csv_factor_pricing(tmp_path, active_factor):
    """price/retail_price come from the factor algorithm, not the raw shop value.

    25.00 * 1.0 + 3.95 (shipping) = 28.95 -> rounded up to next allowed price 29.95.
    """
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "0781491975489", "25,00", "25,00", "10", "BFShirt-XS-BO"],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_csv(rows, str(out))

    data = _read_csv(out)[1]
    # columns: store ean article_number price retail_price quantity
    assert data[3] == "29.95"
    assert data[4] == "29.95"
    assert "," not in data[3] and "," not in data[4]


@pytest.mark.django_db
def test_build_irisone_csv_pimped_zalando_overwrite(tmp_path, active_factor):
    """A Price with pimped_zalando=True uses vk_zalando hard, skipping the factor."""
    Price.objects.create(
        sku="BFShirt-XS-BO",
        vk_zalando="24.99",
        pimped_zalando=True,
        ean="0781491975489",
    )
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "0781491975489", "25,00", "25,00", "10", "BFShirt-XS-BO"],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_csv(rows, str(out))

    data = _read_csv(out)[1]
    assert data[3] == "24.99"
    assert data[4] == "24.99"


@pytest.mark.django_db
def test_build_irisone_csv_price_overwrite(tmp_path, active_factor):
    """A SKU in price_overwrites gets its fixed price and retail_price."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "0781491975489", "25,00", "25,00", "10", "HKB-001"],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_csv(rows, str(out))

    data = _read_csv(out)[1]
    assert data[3] == "26.95"
    assert data[4] == "29.95"


@pytest.mark.django_db
def test_build_irisone_csv_blacklist_skip(tmp_path, active_factor):
    """Blacklisted SKUs are dropped."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            [
                "001",
                "0781491975489",
                "25,00",
                "25,00",
                "10",
                "Hoodie-002",
            ],  # blacklisted
            ["001", "0781491971771", "25,00", "25,00", "3", "BFShirt-XS-BO"],
        ],
    )
    out = tmp_path / "out.csv"

    count = _build_irisone_csv(rows, str(out))

    assert count == 1
    data = _read_csv(out)[1]
    assert data[2] == "BFShirt-XS-BO"


@pytest.mark.django_db
def test_build_irisone_csv_skips_missing_ean_or_article(tmp_path, active_factor):
    """Rows without ean or article_number are skipped."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "", "25,00", "25,00", "10", "BFShirt-XS-BO"],
            ["001", "0781491975489", "25,00", "25,00", "10", ""],
            ["001", "0781491971771", "25,00", "25,00", "3", "JACKET-XS"],
        ],
    )
    out = tmp_path / "out.csv"

    count = _build_irisone_csv(rows, str(out))

    assert count == 1


@pytest.mark.django_db
def test_build_irisone_csv_negative_quantity_clamped(tmp_path, active_factor):
    """Negative quantity is clamped to 0; empty quantity becomes 0."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "0781491975489", "25,00", "25,00", "-4", "BFShirt-XS-BO"],
            ["001", "0781491971771", "25,00", "25,00", "", "JACKET-XS"],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_csv(rows, str(out))

    rows_out = _read_csv(out)
    assert rows_out[1][5] == "0"
    assert rows_out[2][5] == "0"


@pytest.mark.django_db
def test_build_irisone_csv_out_of_season_duplicate(tmp_path, active_factor):
    """Out-of-season articles are duplicated with a fake sku/ean."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            ["store", "ean", "price", "retail_price", "quantity", "article_number"],
            ["001", "0781491975489", "25,00", "25,00", "10", "women-bom-co-m"],
        ],
    )
    out = tmp_path / "out.csv"

    count = _build_irisone_csv(rows, str(out))

    assert count == 2
    rows_out = _read_csv(out)
    assert rows_out[1][2] == "women-bom-co-m"
    assert rows_out[2][1] == "9508355589344"  # fake ean
    assert rows_out[2][2] == "women-bom-co-m-1"  # fake sku
    # duplicate keeps the resolved price
    assert rows_out[2][3] == rows_out[1][3]


# --- product feed ---

SHOP_HEADER = [
    "store",
    "ean",
    "price",
    "retail_price",
    "quantity",
    "article_number",
    "article_color",
    "product_name",
    "store_article_location",
    "product_number",
    "article_size",
]


def _read_product_csv(path):
    rows = _read_csv(path)
    return rows[0], rows[1:]


@pytest.mark.django_db
def test_build_irisone_product_csv_extra_columns(tmp_path, active_factor):
    """Product feed has 15 columns including the 4 ERP mapping columns."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            SHOP_HEADER,
            [
                "001",
                "0781491975489",
                "25,00",
                "25,00",
                "10",
                "BFShirt-XS-BO",
                "Schwarz",
                "Boyfriend T-Shirt",
                "Chop Shop",
                "BFShirt-XS-BO",
                "XS",
            ],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_product_csv(rows, str(out))

    header, data_rows = _read_product_csv(out)
    assert len(header) == 15
    assert header[11] == "erp_ean"
    assert header[12] == "erp_article_number"
    assert header[13] == "erp_article_location"
    assert header[14] == "classification"

    data = data_rows[0]
    assert data[11] == data[header.index("ean")]  # erp_ean == ean
    assert (
        data[12] == data[header.index("article_number")]
    )  # erp_article_number == article_number
    assert data[13] == data[header.index("store_article_location")]
    assert data[14] == "default"


@pytest.mark.django_db
def test_build_irisone_product_csv_factor_pricing(tmp_path, active_factor):
    """Product feed applies factor pricing to price and retail_price."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            SHOP_HEADER,
            [
                "001",
                "0781491975489",
                "25,00",
                "25,00",
                "5",
                "JACKET-XS",
                "Grün",
                "Cord Jacke",
                "Chop Shop",
                "JACKET-XS",
                "XS",
            ],
        ],
    )
    out = tmp_path / "out.csv"

    _build_irisone_product_csv(rows, str(out))

    header, data_rows = _read_product_csv(out)
    data = data_rows[0]
    assert data[header.index("price")] == "29.95"
    assert data[header.index("retail_price")] == "29.95"


@pytest.mark.django_db
def test_build_irisone_product_csv_out_of_season_duplicate(tmp_path, active_factor):
    """Product feed duplicates out-of-season articles with fake sku/ean in erp cols too."""
    rows = _shop_rows(
        tmp_path / "shop.csv",
        [
            SHOP_HEADER,
            [
                "001",
                "0781491975489",
                "25,00",
                "25,00",
                "5",
                "women-bom-co-m",
                "Grün",
                "Bomber",
                "Chop Shop",
                "women-bom-co-m",
                "M",
            ],
        ],
    )
    out = tmp_path / "out.csv"

    count = _build_irisone_product_csv(rows, str(out))

    assert count == 2
    header, data_rows = _read_product_csv(out)
    fake = data_rows[1]
    assert fake[header.index("ean")] == "9508355589344"
    assert fake[header.index("article_number")] == "women-bom-co-m-1"
    assert fake[11] == "9508355589344"  # erp_ean is the fake ean
    assert fake[12] == "women-bom-co-m-1"  # erp_article_number is the fake sku
