import datetime
import hashlib
import json
from decimal import Decimal

import pytest
from django.urls import reverse

from core.models import Category, MarketplaceConfig, Price
from core.services import article_stats
from zalando.models import RawDailyShipmentReport, TransactionFileUpload


def _cleanup():
    TransactionFileUpload.objects.all().delete()
    RawDailyShipmentReport.objects.all().delete()
    MarketplaceConfig.objects.all().delete()


@pytest.mark.django_db
def test_article_stats_zalando_basic():
    """Basic test with small data set."""
    _cleanup()

    # Config has to be in charge before the import
    config = MarketplaceConfig.objects.create(
        name=article_stats.Marketplace.ZALANDO,
        shipping_costs=Decimal("3.55"),
        return_costs=Decimal("3.55"),
        provision_in_percent=None,
        vat_in_percent=19,
        generic_costs_in_percent=3,
    )

    fixtures = [
        ("core/tests/fixtures/core_category.json", Category),
        ("core/tests/fixtures/core_price.json", Price),
        (
            "core/tests/fixtures/raw_dailyshipment_report.small.json",
            RawDailyShipmentReport,
        ),
    ]
    for fixture_file, model in fixtures:
        with open(fixture_file) as f:
            file_contents = f.read()
            data = json.loads(file_contents)
            for fields in data:
                model.objects.create(**fields)

    RawDailyShipmentReport.objects.all().update(marketplace_config=config)

    test_date = datetime.date(2023, 2, 14)
    stats = article_stats.get_article_stats(
        test_date, article_stats.Marketplace.ZALANDO
    )
    assert stats == {
        "Woman Bomber Jacken": {
            "content": [
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("12.13"),
                    "eight_percent_provision": Decimal("1.43"),
                    "generic_costs": Decimal("0.84"),
                    "nineteen_percent_vat": Decimal("4.46"),
                    "profit_after_taxes": Decimal("5.54"),
                    "return_costs": Decimal("3.55"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("-7.94"),
                    "total_return_costs": Decimal("7.94"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("27.95"),
                }
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 1,
                "sales": Decimal("0.00"),
                "shipped": 0,
                "total_diff": Decimal("-7.94"),
                "total_return_costs": Decimal("7.94"),
                "total_revenue": Decimal("0.00"),
            },
        }
    }

    test_date = datetime.date(2023, 2, 12)
    stats = article_stats.get_article_stats(
        test_date, article_stats.Marketplace.ZALANDO
    )
    assert stats == {
        "Woman Bomber Jacken": {
            "content": [
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("12.13"),
                    "eight_percent_provision": Decimal("1.43"),
                    "generic_costs": Decimal("0.84"),
                    "nineteen_percent_vat": Decimal("4.46"),
                    "profit_after_taxes": Decimal("5.54"),
                    "return_costs": Decimal("3.55"),
                    "returned": 2,
                    "sales": Decimal("55.90"),
                    "shipped": 2,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("-15.88"),
                    "total_return_costs": Decimal("15.88"),
                    "total_revenue": Decimal("-0.00"),
                    "vk_zalando": Decimal("27.95"),
                }
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 2,
                "sales": Decimal("55.90"),
                "shipped": 2,
                "total_diff": Decimal("-15.88"),
                "total_return_costs": Decimal("15.88"),
                "total_revenue": Decimal("0.00"),
            },
        }
    }

    test_date = datetime.date(2023, 1, 1)
    stats = article_stats.get_article_stats(
        test_date, article_stats.Marketplace.ZALANDO
    )
    assert stats == {
        "Woman Bomber Jacken": {
            "content": [
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("12.13"),
                    "eight_percent_provision": Decimal("1.43"),
                    "generic_costs": Decimal("0.84"),
                    "nineteen_percent_vat": Decimal("4.46"),
                    "profit_after_taxes": Decimal("5.54"),
                    "return_costs": Decimal("3.55"),
                    "returned": 2,
                    "sales": Decimal("139.75"),
                    "shipped": 5,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("0.74"),
                    "total_return_costs": Decimal("15.88"),
                    "total_revenue": Decimal("16.62"),
                    "vk_zalando": Decimal("27.95"),
                },
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("12.13"),
                    "eight_percent_provision": Decimal("1.22"),
                    "generic_costs": Decimal("0.72"),
                    "nineteen_percent_vat": Decimal("3.82"),
                    "profit_after_taxes": Decimal("2.51"),
                    "return_costs": Decimal("3.55"),
                    "returned": 0,
                    "sales": Decimal("47.90"),
                    "shipped": 2,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("5.02"),
                    "total_return_costs": Decimal("0.00"),
                    "total_revenue": Decimal("5.02"),
                    "vk_zalando": Decimal("23.95"),
                },
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 2,
                "sales": Decimal("187.65"),
                "shipped": 7,
                "total_diff": Decimal("5.76"),
                "total_return_costs": Decimal("15.88"),
                "total_revenue": Decimal("21.64"),
            },
        }
    }


def test_different_configs_reflected_in_stats(
    client, django_user_model, django_db_setup
):
    """Article stats join marketplace configuration."""
    _cleanup()

    category = Category.objects.create(name="example_category")
    skus = [
        "pizza_2_w-l",
        "stra_wings_w-l",
        "women-bom-da-l",
        "women-bom-vi-s",
        "Knit-Set-BL",
        "KLOOP-NA",
        "duffel-sand",
        "BM013-FBM",
    ]
    for sku in skus:
        Price.objects.create(
            sku=sku,
            category=category,
            costs_production=Decimal("10.42"),
            vk_otto=Decimal("23.99"),
            vk_zalando=Decimal("100.00"),
        )

    #
    # 0 - First upload of files - reference to the current marketplace configuration
    #
    config1 = MarketplaceConfig.objects.create(
        name=article_stats.Marketplace.ZALANDO,
        shipping_costs=Decimal("1.11"),
        return_costs=Decimal("1.11"),
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
        fp = open(f"zalando/tests/fixtures/daily_sales_report_{idx}.csv", "rb")
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
        shipping_costs=Decimal("2.22"),
        return_costs=Decimal("2.22"),
        provision_in_percent=None,
        vat_in_percent=7,
        generic_costs_in_percent=5,
    )
    original_files = []
    original_files_md5sums = []
    for idx in [2, 3]:
        fp = open(f"zalando/tests/fixtures/daily_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    stats = article_stats.get_article_stats_zalando("2020-01-01")

    assert (
        stats["example_category"]["content"][0]["shipping_costs"]
        == config1.shipping_costs
    )
    assert (
        stats["example_category"]["content"][0]["return_costs"] == config1.return_costs
    )

    assert (
        stats["example_category"]["content"][-1]["shipping_costs"]
        == config2.shipping_costs
    )
    assert (
        stats["example_category"]["content"][-1]["return_costs"] == config2.return_costs
    )
