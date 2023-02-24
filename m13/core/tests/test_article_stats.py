import datetime
import json
from decimal import Decimal

import pytest

from core.models import Category, MarketplaceConfig, Price
from core.services.article_stats import Marketplace, get_article_stats
from zalando.models import RawDailyShipmentReport


@pytest.mark.django_db
def test_article_stats_zalando_basic():
    """Basic test with small data set."""
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

    MarketplaceConfig.objects.create(
        name=Marketplace.ZALANDO,
        shipping_costs=Decimal("3.55"),
        return_costs=Decimal("3.55"),
        provision_in_percent=None,
        vat_in_percent=19,
        generic_costs_in_percent=3,
    )

    test_date = datetime.date(2023, 1, 1)
    article_stats = get_article_stats(test_date, Marketplace.ZALANDO)

    assert article_stats == {
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
    article_stats = get_article_stats(test_date, Marketplace.ZALANDO)
    assert article_stats == {
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
    article_stats = get_article_stats(test_date, Marketplace.ZALANDO)
    assert article_stats == {
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
