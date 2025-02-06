from django.db import connection
from rest_framework import permissions, viewsets

from m13.lib.psql import dictfetchall

from .models import SalesStatsReturnTop13, SalesStatsTop13, SalesVolumeZalando
from .serializers import (
    SalesStatsReturnTop13Serializer,
    SalesStatsTop13Serializer,
    SalesVolumeZalandoSerializer,
)


class SalesStatsTop13ViewSet(viewsets.ModelViewSet):
    """API endpoint to receive top sales by sku."""

    queryset = SalesStatsTop13.objects.all()
    serializer_class = SalesStatsTop13Serializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return data filtered by date range."""
        result = []
        params = {
            "start_date": self.request.query_params.get("from"),
            "end_date": self.request.query_params.get("to"),
        }
        with connection.cursor() as cursor:
            query = """
                SELECT
                    1 as id,
                    cc.name as category_name,
                    cp.sku as sku,
                    COUNT(1) FILTER ( WHERE msr.shipment_type = 'Sale' ) as shipped

                FROM
                    zalando_monthly_sales_report as msr
                JOIN core_price AS cp
                    ON cp.ean = msr.ean
                JOIN core_category AS cc
                    on cc.id = cp.category_id
                WHERE
                    msr.order_date >= %(start_date)s
                    AND msr.order_date <= %(end_date)s
                GROUP BY
                    category_name,
                    sku
                ORDER BY shipped DESC
                LIMIT 13;

            """
            cursor.execute(query, params)
            for entry in dictfetchall(cursor):
                result.append(entry)

        return result


class SalesStatsTop13ReturnViewSet(viewsets.ModelViewSet):
    """API endpoint to receive top returned articles by sku."""

    queryset = SalesStatsReturnTop13.objects.all()
    serializer_class = SalesStatsReturnTop13Serializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return data filtered by date range."""
        result = []
        params = {
            "start_date": self.request.query_params.get("from"),
            "end_date": self.request.query_params.get("to"),
        }
        with connection.cursor() as cursor:
            query = """
                SELECT
                    1 as id,
                    cc.name as category_name,
                    cp.sku as sku,
                    COUNT(1) FILTER ( WHERE msr.shipment_type <> 'Sale' ) as returned

                FROM
                    zalando_monthly_sales_report as msr
                JOIN core_price AS cp
                    ON cp.ean = msr.ean
                JOIN core_category AS cc
                    on cc.id = cp.category_id
                WHERE
                    msr.order_date >= %(start_date)s
                    AND msr.order_date <= %(end_date)s
                GROUP BY
                    category_name,
                    sku
                ORDER BY returned DESC
                LIMIT 13;

            """
            cursor.execute(query, params)
            for entry in dictfetchall(cursor):
                result.append(entry)

        return result


class SalesVolumeZalandoViewSet(viewsets.ModelViewSet):
    """API endpoint to receive sales volume of zalando for given time range."""

    queryset = SalesVolumeZalando.objects.all()
    serializer_class = SalesVolumeZalandoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return data filtered by date range."""
        result = []
        params = {
            "start_date": self.request.query_params.get("from"),
            "end_date": self.request.query_params.get("to"),
        }
        with connection.cursor() as cursor:
            query = """
                SELECT
                    1 as id,
                    COALESCE(SUM(msr.price) FILTER (WHERE msr.shipment_type = 'Sale'), 0) AS sum_sales,
                    -- date_trunc('week', msr.order_date) as week
                    CONCAT(DATE_PART('year', msr.order_date), '-', LPAD(DATE_PART('week', msr.order_date)::text, 2, '0')) AS week
                FROM
                    zalando_monthly_sales_report as msr
                WHERE
                    msr.order_date >= %(start_date)s
                    AND msr.order_date <= %(end_date)s
                GROUP BY
                    week
                ORDER BY
                    week
            """
            cursor.execute(query, params)
            for entry in dictfetchall(cursor):
                result.append(entry)

        return result
