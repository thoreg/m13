"""Tests for irisone.services.feed._build_irisone_csv."""
import csv

from irisone.services.feed import _build_irisone_csv


def _write_shop_csv(path, rows):
    with open(path, "w", encoding="UTF-8", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)


def test_build_irisone_csv_decimal_separator(tmp_path):
    """German comma decimals are converted to dots."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        ["store", "ean", "price", "retail_price", "quantity", "article_number"],
        ["001", "0781491975489", "27,95", "27,95", "10", "BFShirt-XS-BO"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_csv(list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")), str(out))

    with open(out, "r", encoding="UTF-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    data = rows[1]
    assert "," not in data[3], "irisOne price must use dot as decimal separator"
    assert "," not in data[4], "irisOne retail_price must use dot as decimal separator"
    assert data[3] == "27.95"
    assert data[4] == "27.95"


def test_build_irisone_csv_retail_price_fallback(tmp_path):
    """retail_price falls back to price when shop retail_price is empty."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        ["store", "ean", "price", "retail_price", "quantity", "article_number"],
        ["001", "0781491975489", "27,95", "", "10", "BFShirt-XS-BO"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_csv(list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")), str(out))

    with open(out, "r", encoding="UTF-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    data = rows[1]
    # Both price columns must have a value
    assert data[3] != "", "irisOne price must not be empty"
    assert data[4] != "", "irisOne retail_price must not be empty"
    assert data[3] == "27.95"
    assert data[4] == "27.95"


def test_build_irisone_csv_column_mapping(tmp_path):
    """shop price → irisOne retail_price; shop retail_price → irisOne price."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        ["store", "ean", "price", "retail_price", "quantity", "article_number"],
        ["001", "0781491975489", "49,95", "39,95", "5", "JACKET-XS"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_csv(list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")), str(out))

    with open(out, "r", encoding="UTF-8") as f:
        rows = list(csv.reader(f, delimiter=";"))

    header = rows[0]
    data = rows[1]
    price_idx = header.index("price")
    retail_price_idx = header.index("retail_price")

    # irisOne price = shop retail_price (PP/sale price)
    assert data[price_idx] == "39.95"
    # irisOne retail_price = shop price (regular price)
    assert data[retail_price_idx] == "49.95"


def test_build_irisone_csv_skips_missing_ean_or_article(tmp_path):
    """Rows without ean or article_number are skipped."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        ["store", "ean", "price", "retail_price", "quantity", "article_number"],
        ["001", "", "27,95", "27,95", "10", "BFShirt-XS-BO"],
        ["001", "0781491975489", "27,95", "27,95", "10", ""],
        ["001", "0781491971771", "49,95", "49,95", "3", "JACKET-XS"],
    ])
    out = tmp_path / "out.csv"

    count = _build_irisone_csv(
        list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")),
        str(out),
    )

    assert count == 1
