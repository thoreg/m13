from m13.lib.csv_reader import read_csv
from zalando.models import DailyShipmentReport, TransactionFileUpload


def import_all_unprocessed_daily_shipment_reports():
    """..."""
    files = TransactionFileUpload.objects.filter(processed=False)
    for file in files:
        import_daily_shipment_report(file.original_csv.name)


def import_daily_shipment_report(path):
    """Import daily shipment report data for further analytics and reports."""
    for line in read_csv(path, delimiter=","):

        canceled = line['Cancellation'] == 'x'
        returned = line['Return'] == 'x'
        shipped = line['Shipment'] == 'x'

        price_in_cent = float(line['Price']) * 100

        DailyShipmentReport.objects.get_or_create(
            article_number=line['Article Number'], defaults=dict(
                cancel=canceled,
                channel_order_number=line['Channel Order Number'],
                order_created=line['Order Created'],
                price_in_cent=price_in_cent,
                return_reason=line['Return Reason'],
                returned=returned,
                shipment=shipped))
