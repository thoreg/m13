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
                    "costs_production": Decimal("23.13"),
                    "eight_percent_provision": Decimal("7.06"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.82"),
                    "return_costs": Decimal("3.55"),
                    "returned": 0,
                    "sales": Decimal("279.80"),
                    "shipped": 4,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("83.28"),
                    "total_return_costs": Decimal("0.00"),
                    "total_revenue": Decimal("83.28"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "eight_percent_provision": Decimal("6.56"),
                    "generic_costs": Decimal("1.95"),
                    "nineteen_percent_vat": Decimal("12.34"),
                    "profit_after_taxes": Decimal("17.42"),
                    "return_costs": Decimal("3.55"),
                    "returned": 2,
                    "sales": Decimal("194.85"),
                    "shipped": 3,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("-0.68"),
                    "total_return_costs": Decimal("18.10"),
                    "total_revenue": Decimal("17.42"),
                    "vk_zalando": Decimal("64.95"),
                },
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 2,
                "sales": Decimal("474.65"),
                "shipped": 7,
                "total_diff": Decimal("82.60"),
                "total_return_costs": Decimal("18.10"),
                "total_revenue": Decimal("100.70"),
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
                    "costs_production": Decimal("23.13"),
                    "eight_percent_provision": Decimal("7.06"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.82"),
                    "return_costs": Decimal("3.55"),
                    "returned": 0,
                    "sales": Decimal("139.90"),
                    "shipped": 2,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("41.64"),
                    "total_return_costs": Decimal("0.00"),
                    "total_revenue": Decimal("41.64"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "eight_percent_provision": Decimal("6.56"),
                    "generic_costs": Decimal("1.95"),
                    "nineteen_percent_vat": Decimal("12.34"),
                    "profit_after_taxes": Decimal("17.42"),
                    "return_costs": Decimal("3.55"),
                    "returned": 2,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("-52.94"),
                    "total_return_costs": Decimal("18.10"),
                    "total_revenue": Decimal("-34.84"),
                    "vk_zalando": Decimal("64.95"),
                },
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 2,
                "sales": Decimal("139.90"),
                "shipped": 2,
                "total_diff": Decimal("-11.30"),
                "total_return_costs": Decimal("18.10"),
                "total_revenue": Decimal("6.80"),
            },
        }
    }

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
                    "costs_production": Decimal("23.13"),
                    "eight_percent_provision": Decimal("6.56"),
                    "generic_costs": Decimal("1.95"),
                    "nineteen_percent_vat": Decimal("12.34"),
                    "profit_after_taxes": Decimal("17.42"),
                    "return_costs": Decimal("3.55"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.55"),
                    "total_diff": Decimal("-26.47"),
                    "total_return_costs": Decimal("9.05"),
                    "total_revenue": Decimal("-17.42"),
                    "vk_zalando": Decimal("64.95"),
                }
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 1,
                "sales": Decimal("0.00"),
                "shipped": 0,
                "total_diff": Decimal("-26.47"),
                "total_return_costs": Decimal("9.05"),
                "total_revenue": Decimal("-17.42"),
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
