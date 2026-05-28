"""Tests for irisone.services.feed._build_irisone_csv and _build_irisone_product_csv."""
import csv

from irisone.services.feed import _build_irisone_csv, _build_irisone_product_csv


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


# --- product feed ---

SHOP_HEADER = [
    "store", "ean", "price", "retail_price", "quantity",
    "article_number", "article_color", "product_name",
    "store_article_location", "product_number", "article_size",
]


def _read_product_csv(path):
    with open(path, "r", encoding="UTF-8") as f:
        rows = list(csv.reader(f, delimiter=";"))
    header = rows[0]
    return header, rows[1:]


def test_build_irisone_product_csv_extra_columns(tmp_path):
    """Product feed has 15 columns including the 4 ERP mapping columns."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        SHOP_HEADER,
        ["001", "0781491975489", "49,95", "49,95", "10",
         "BFShirt-XS-BO", "Schwarz", "Boyfriend T-Shirt", "Chop Shop", "BFShirt-XS-BO", "XS"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_product_csv(
        list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")),
        str(out),
    )

    header, rows = _read_product_csv(out)
    assert len(header) == 15
    assert header[11] == "erp_ean"
    assert header[12] == "erp_article_number"
    assert header[13] == "erp_store_article_location"
    assert header[14] == "classification"

    data = rows[0]
    assert data[11] == data[header.index("ean")]   # erp_ean == ean
    assert data[12] == data[header.index("article_number")]  # erp_article_number == article_number
    assert data[13] == data[header.index("store_article_location")]
    assert data[14] == "default"


def test_build_irisone_product_csv_decimal_and_price_mapping(tmp_path):
    """Product feed applies decimal fix and price/retail_price swap."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        SHOP_HEADER,
        ["001", "0781491975489", "49,95", "39,95", "5",
         "JACKET-XS", "Grün", "Cord Jacke", "Chop Shop", "JACKET-XS", "XS"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_product_csv(
        list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")),
        str(out),
    )

    header, rows = _read_product_csv(out)
    data = rows[0]
    price_idx = header.index("price")
    retail_price_idx = header.index("retail_price")

    assert data[price_idx] == "39.95"    # shop retail_price → irisOne price
    assert data[retail_price_idx] == "49.95"  # shop price → irisOne retail_price


def test_build_irisone_product_csv_retail_price_fallback(tmp_path):
    """Product feed fills empty retail_price with price value."""
    shop_csv = tmp_path / "shop.csv"
    _write_shop_csv(shop_csv, [
        SHOP_HEADER,
        ["001", "0781491975489", "49,95", "", "5",
         "JACKET-XS", "Grün", "Cord Jacke", "Chop Shop", "JACKET-XS", "XS"],
    ])
    out = tmp_path / "out.csv"

    _build_irisone_product_csv(
        list(csv.reader(shop_csv.read_text(encoding="UTF-8").splitlines(), delimiter=";")),
        str(out),
    )

    header, rows = _read_product_csv(out)
    data = rows[0]
    price_idx = header.index("price")
    retail_price_idx = header.index("retail_price")

    assert data[price_idx] == "49.95"
    assert data[retail_price_idx] == "49.95"
