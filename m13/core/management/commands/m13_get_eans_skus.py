"""Receive all skus+eans from the db."""
import django
from django.core.management.base import BaseCommand

from core.models import Price
from otto.models import OrderItem as otto_oi
from zalando.models import OrderItem as z_oi


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **kwargs):
        """..."""
        otto_by_ean = {}
        otto_by_sku = {}
        z_by_ean = {}
        z_by_sku = {}

        all_otto_ois = otto_oi.objects.all()
        all_z_ois = z_oi.objects.all()

        for oi in all_otto_ois:
            if oi.ean not in otto_by_ean:
                otto_by_ean[oi.ean] = (oi.sku, oi.product_title)
            if oi.sku not in otto_by_sku:
                otto_by_sku[oi.sku] = (
                    oi.ean,
                    oi.product_title,
                )

        for oi in all_z_ois:
            if oi.ean not in z_by_ean:
                z_by_ean[oi.ean] = []
            z_by_ean[oi.ean].append((oi.article_number, oi.created))

            if oi.article_number not in z_by_sku:
                z_by_sku[oi.article_number] = (
                    oi.ean,
                    oi.created,
                )

        # Not fixable: different EANs Otto vs Z
        # print("check by z_sku")
        # for z_sku in z_by_sku:
        #     try:
        #         otto_ean = otto_by_sku[z_sku]
        #     except KeyError:
        #         # print(f"z_sku: {z_sku} not known by otto")
        #         continue

        #     # if not otto_ean[0] == z_by_sku[z_sku]:
        #     #     msg = "EANs different - "
        #     #     msg += f"z_sku: {z_sku} otto_ean: {otto_ean[0]}"
        #     #     msg += f" z_ean: {z_by_sku[z_sku]}"
        #     #     print(msg)

        eans = []
        duplicated_eans = []
        for z_sku in z_by_sku:
            ean = z_by_sku[z_sku][0]
            try:
                price = Price.objects.get(sku=z_sku)
                price.ean = ean
                try:
                    price.save()
                except django.db.utils.IntegrityError:
                    print(
                        f"EAN doppelt vergeben: {ean} :",
                    )
                    # for oi in z_by_ean[ean]:
                    #     print(f"    oi: {oi}")

            except Price.DoesNotExist:
                print(f"No price found for {z_sku}")
                continue

            if ean in eans:
                duplicated_eans.append((ean, z_sku))
            else:
                eans.append(ean)

        print("\n\nprices without ean:")
        prices_without_eans = Price.objects.filter(ean__isnull=True)
        for price in prices_without_eans:
            print(f"{price.sku} : {price.category}")
            try:
                ean = otto_by_sku[price.sku][0]
                price.ean = ean
                price.save()
                print(f"SKU {price.sku} fixed with EAN from otto")
            except KeyError:
                pass
            except Exception as exc:
                print(exc)
                # import ipdb; ipdb.set_trace()

        # print("\n\nduplicated ean at Z:")
        # for ean in duplicated_eans:
        #     print(ean)
        prices_without_eans = Price.objects.filter(ean__isnull=True)
        print("\n\nprices without ean (after otto fix):")
        for price in prices_without_eans:
            print(f"{price.sku} : {price.category}")

        print(f"\n\nprices without ean: {prices_without_eans.count()}")
