import csv


def dump_result_to_file(result_rows: list, path: str = "result.csv"):
    """Write out list of rows into csv on disk."""
    EXPORT_FIELDS = [
        "Umsatz (ohne Soll/Haben-Kz)",  # Brutto Verkaufspreis
        "Soll/Haben-Kennzeichen",  # S (Verkauf) | H (Retoure)
        "WKZ Umsatz",  # Waehrung
        "Kurs",  # Wechselkurs falls verfugbar
        "Basis-Umsatz",  # Betrag
        "WKZ Basis-Umsatz",  # EUR
        "Konto",  # Verrechnungskonto (ACCOUNTING_MAP)
        "Gegenkonto (ohne BU-Schlüssel)",  # Erloes/Aufwandskonto
        "BU-Schlüssel",  # 9 wenn Verrechnungskonto 3101
        "Belegdatum",  # Verkaufsdatum ohne punkt (wtf) DDMM
        "Belegfeld 1",  # OrderID
        "Belegfeld 2",  #
        "Skonto",  #
        "Buchungstext",  # Beliebiger Text
    ]
    with open(path, "w", encoding="UTF8") as fd:
        csv_writer = csv.DictWriter(
            fd, EXPORT_FIELDS, delimiter=";", escapechar="\\", quoting=csv.QUOTE_ALL
        )
        csv_writer.writeheader()
        csv_writer.writerows(result_rows)
