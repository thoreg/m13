"""Take info like price and pimped flag from ZProduct and apply it to core.Price."""

from django.core.management.base import BaseCommand

from core.models import Price
from zalando.models import ZProduct


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **kwargs):
        """..."""
        zproducts = ZProduct.objects.all().values()
        zproducts_by_article = {zp["article"]: zp for zp in zproducts}

        no_price_products = []
        not_pimped = []

        for sku, zp in zproducts_by_article.items():
            try:
                price = Price.objects.get(sku=sku)
                zp_price = zp["vk_zalando"]
                if price.vk_zalando != zp_price:
                    print(f"{sku} - {price.vk_zalando} VS {zp_price} - DIFF")
                else:
                    print(f"{sku} - {price.vk_zalando} - OK")

                if price.vk_zalando is None:
                    no_price_products.append(sku)

                if zp["pimped"] is not True:
                    not_pimped.append(sku)
                else:
                    price.pimped_zalando = True
                    price.save()

            except Price.DoesNotExist:
                print(f"{sku} - no price")

        print("The following products have no price:")
        for p in no_price_products:
            print(p)

        print("The following products are not pimped:")
        for np in not_pimped:
            print(np)
