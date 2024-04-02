import datetime
import hashlib
import json
from decimal import Decimal
from pprint import pprint

import pytest
from django.core.management import call_command
from django.urls import reverse

from core.models import Category, MarketplaceConfig, Price
from core.services import article_stats
from core.services.article_stats import (
    OTTO_PROVISION_IN_PERCENT,
    ArticleStats,
    Marketplace,
)
from otto.models import OrderItem as otto_oi
from otto.models import OrderItemJournal
from zalando.models import SalesReport, SalesReportFileUpload


def _cleanup():
    """..."""
    SalesReport.objects.all().delete()
    SalesReportFileUpload.objects.all().delete()
    Price.objects.all().delete()
    MarketplaceConfig.objects.all().delete()
    Price.objects.all().delete()
    Category.objects.all().delete()


@pytest.mark.django_db
def test_article_stats_zalando_basic(django_db_setup, django_db_blocker):
    """Basic test with small data set."""

    _cleanup()
    fixtures = [
        "zalando/tests/fixtures/core.Category.json",
        "zalando/tests/fixtures/core.Price.json",
        "zalando/tests/fixtures/core.MarketplaceConfig.json",
        "zalando/tests/fixtures/zalando.SalesReportFileUpload.json",
        "zalando/tests/fixtures/zalando.SalesReport.json",
    ]
    with django_db_blocker.unblock():
        for fixture in fixtures:
            call_command("loaddata", fixture)

    start_date = datetime.date(2023, 3, 15)
    end_date = datetime.date(2023, 4, 1)
    stats = article_stats.get_article_stats(
        article_stats.Marketplace.ZALANDO, start_date, end_date
    )

    assert stats == {
        "Acid Washed Jacke": {
            "content": [
                {
                    "article_number": "WOJacke-HE-L",
                    "canceled": 0,
                    "category": "Acid Washed Jacke",
                    "costs_production": Decimal("31.13"),
                    "generic_costs": Decimal("1.95"),
                    "nineteen_percent_vat": Decimal("12.34"),
                    "profit_after_taxes": Decimal("9.17"),
                    "provision": Decimal("6.56"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-9.93"),
                    "total_return_costs": Decimal("9.93"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("64.95"),
                }
            ],
            "name": "Acid Washed Jacke",
            "stats": {
                "canceled": 0,
                "returned": 1,
                "sales": Decimal("0.00"),
                "shipped": 0,
                "total_diff": Decimal("-9.93"),
                "total_return_costs": Decimal("9.93"),
                "total_revenue": Decimal("0.00"),
            },
        },
        "Bucket Hats": {
            "content": [
                {
                    "article_number": "BUHA-BOL",
                    "canceled": 0,
                    "category": "Bucket Hats",
                    "costs_production": Decimal("20.82"),
                    "generic_costs": Decimal("1.05"),
                    "nineteen_percent_vat": Decimal("6.64"),
                    "profit_after_taxes": Decimal("0.86"),
                    "provision": Decimal("1.78"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-9.03"),
                    "total_return_costs": Decimal("9.03"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("34.95"),
                }
            ],
            "name": "Bucket Hats",
            "stats": {
                "canceled": 0,
                "returned": 1,
                "sales": Decimal("0.00"),
                "shipped": 0,
                "total_diff": Decimal("-9.03"),
                "total_return_costs": Decimal("9.03"),
                "total_revenue": Decimal("0.00"),
            },
        },
        "Woman Bomber Jacken": {
            "content": [
                {
                    "article_number": "women-bom-bo-l",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-bo-m",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-bo-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-na-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("69.95"),
                    "shipped": 1,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-na-xl",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-vi-m",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 0,
                    "sales": Decimal("69.95"),
                    "shipped": 1,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("20.57"),
                    "total_return_costs": Decimal("0.00"),
                    "total_revenue": Decimal("20.57"),
                    "vk_zalando": Decimal("69.95"),
                },
                {
                    "article_number": "women-bom-vi-s",
                    "canceled": 0,
                    "category": "Woman Bomber Jacken",
                    "costs_production": Decimal("23.13"),
                    "generic_costs": Decimal("2.10"),
                    "nineteen_percent_vat": Decimal("13.29"),
                    "profit_after_taxes": Decimal("20.57"),
                    "provision": Decimal("7.06"),
                    "return_costs": Decimal("4.18"),
                    "returned": 1,
                    "sales": Decimal("0.00"),
                    "shipped": 0,
                    "shipping_costs": Decimal("3.80"),
                    "total_diff": Decimal("-10.08"),
                    "total_return_costs": Decimal("10.08"),
                    "total_revenue": Decimal("0.00"),
                    "vk_zalando": Decimal("69.95"),
                },
            ],
            "name": "Woman Bomber Jacken",
            "stats": {
                "canceled": 0,
                "returned": 6,
                "sales": Decimal("139.90"),
                "shipped": 2,
                "total_diff": Decimal("-39.91"),
                "total_return_costs": Decimal("60.48"),
                "total_revenue": Decimal("20.57"),
            },
        },
    }


@pytest.mark.django_db
def test_different_configs_reflected_in_stats(
    client, django_user_model, django_db_setup, django_db_blocker
):
    """Article stats join marketplace configuration."""

    _cleanup()

    fixtures = [
        "zalando/tests/fixtures/core.Category.json",
        "zalando/tests/fixtures/core.Price.json",
        "zalando/tests/fixtures/core.MarketplaceConfig.json",
        "zalando/tests/fixtures/zalando.SalesReportFileUpload.json",
        "zalando/tests/fixtures/zalando.SalesReport.json",
    ]
    with django_db_blocker.unblock():
        for fixture in fixtures:
            call_command("loaddata", fixture)

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
        fp = open(f"zalando/tests/fixtures/monthly_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    stats = article_stats.get_article_stats_zalando_msr_based(
        "2023-09-01", "2024-02-01"
    )

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
        fp = open(f"zalando/tests/fixtures/monthly_sales_report_{idx}.csv", "rb")
        content = fp.read()
        md5_hash = hashlib.md5()
        md5_hash.update(content)
        fp.seek(0)

        original_files.append(fp)
        original_files_md5sums.append(md5_hash.hexdigest())

    response = client.post(upload_url, {"original_csv": original_files})

    stats = article_stats.get_article_stats_zalando_msr_based(
        "2023-09-01", "2024-02-01"
    )
    assert (
        stats["Boyfriend Shirts"]["content"][0]["shipping_costs"]
        == config1.shipping_costs
    )
    assert (
        stats["Boyfriend Shirts"]["content"][0]["return_costs"] == config1.return_costs
    )

    assert (
        stats["Double Sided Beanies"]["content"][-1]["shipping_costs"]
        == config2.shipping_costs
    )
    assert (
        stats["Double Sided Beanies"]["content"][-1]["return_costs"]
        == config2.return_costs
    )


@pytest.mark.django_db
def test_article_stats_otto_basic():
    """Basic test with small data set for ocalculator."""
    # Note id needs to be '3' for otto stats :(
    MarketplaceConfig.objects.create(
        id=3,
        name=article_stats.Marketplace.OTTO,
        shipping_costs=Decimal("3.55"),
        return_costs=Decimal("3.55"),
        provision_in_percent=None,
        vat_in_percent=19,
        generic_costs_in_percent=3,
    )

    fixtures = [
        ("core/tests/fixtures/core_category.json", Category),
        ("core/tests/fixtures/core_price.json", Price),
    ]
    for fixture_file, model in fixtures:
        with open(fixture_file) as f:
            file_contents = f.read()
            data = json.loads(file_contents)
            for fields in data:
                model.objects.create(**fields)

    call_command("m13_otto_sync_orderitem_history", "2")
    assert OrderItemJournal.objects.all().count() == 113

    start_date = datetime.date(2020, 2, 14)
    end_date = datetime.date(2023, 3, 13)
    stats = article_stats.get_article_stats(
        article_stats.Marketplace.OTTO, start_date, end_date
    )

    def __debug():
        print("orderitems_start")
        for oi in otto_oi.objects.all():
            pprint(oi)
        print("orderitems_end")

        print("stats_start")
        pprint(stats)
        print("stats_end")

    # __debug()

    with open("core/tests/expected/otto_stats.json", encoding="utf-8") as f:
        file_contents = f.read()
        excpected_otto_stats = json.loads(file_contents)

    # Take all the Decimal() values and convert them into string to allow
    # comparison with the dumped json
    def __decimal2str(d):
        for k, v in d.items():
            if isinstance(v, dict):
                __decimal2str(v)
            elif isinstance(v, list):
                for element in v:
                    __decimal2str(element)
            else:
                if isinstance(v, Decimal):
                    d[k] = str(v)

    __decimal2str(stats)

    assert stats == excpected_otto_stats


def test_article_stats_basic():
    """Dataclass works as expected with all its properties."""
    astats = ArticleStats(
        sku="example_sku",
        category="example_category",
        marketplace=Marketplace.OTTO,
        price=Decimal("100.00"),
        provision_in_percent=OTTO_PROVISION_IN_PERCENT,
        vat_in_percent=19,
        generic_costs_in_percent=3,
        production_costs=Decimal("33"),
        shipping_costs=Decimal("3"),
        return_costs=Decimal("4"),
        shipped=1,
        returned=0,
    )
    assert astats.provision_amount == Decimal("15.00")
    assert astats.vat_amount == Decimal("19.00")
    assert astats.generic_costs_amount == Decimal("3.00")
    assert astats.profit_after_taxes == Decimal("27.00")
