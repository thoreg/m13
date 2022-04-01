"""CSV related utility functions live here."""
import csv


def read_csv(filename, delimiter=";"):
    """Read given filename and return lines as generator."""
    with open(filename, "r", encoding='utf8') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=delimiter)
        yield next(datareader)  # yield the header row
        for row in datareader:
            yield row
