"""Script to anonymize data in a given fixture."""
import json
import random
import string
from argparse import ArgumentParser
from pprint import pprint


def _get_random_name():
    """Return a random name."""
    names = [
        "Al Cohol",
        "Andi Tafel",
        "Ben Zin",
        "Christian Steifen",
        "Dennis Ochejal",
        "Good Night Anderson",
        "Inge Nieur",
        "Lasse Reinboeng",
        "Metfist Willi",
        "Timo Beil",
        "Tom Bola",
    ]

    name = names[random.randint(0, len(names) - 1)]
    return f"{name}"


def _get_random_email():
    """Return a random email address."""
    names = [
        "al_cohol",
        "andi_tafel",
        "ben_zin",
        "christian_steifen",
        "dennis_ochejal",
        "good_night_anderson",
        "inge_nieur",
        "metfist_willi",
        "timo_beil",
        "tom_bola",
    ]
    domains = [
        "abc.com",
        "aol.com",
        "bing.com",
        "foo.bar",
        "github.com",
        "gitlab.com",
        "gmail.com",
    ]

    name = names[random.randint(0, len(names) - 1)]
    domain = domains[random.randint(0, len(domains) - 1)]

    return f"{name}@{domain}"


def _get_random_id():
    """Return a random id with 8-9 digits."""
    return random.randint(10000000, 999999999)


def _get_random_address():
    """Make some random noice."""
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits + "\n")
        for _ in range(100)
    )


# Name of fields which might contain PII which should be replaced (anonymized)
ANONYMIZER_MAP = {
    "buyer_email": _get_random_email,
    "buyer_user_id": _get_random_id,
    "formatted_address": _get_random_address,
    "first_line": _get_random_address,
    "second_line": _get_random_address,
    "name": _get_random_name,
}


def process(data):
    """Substitute values of dedicated keys and return the updated data."""
    for entry in data:
        print(entry)
        if "fields" in entry:
            for key, value in entry["fields"].items():
                try:
                    entry["fields"][key] = ANONYMIZER_MAP[key]()
                except KeyError:
                    if key in ANONYMIZER_MAP:
                        print(f"unexpected key error - key: {key}")
        else:
            for key in entry:
                try:
                    entry[key] = ANONYMIZER_MAP[key]()
                except KeyError:
                    if key in ANONYMIZER_MAP:
                        print(f"unexpected key error - key: {key}")
    return data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file name", required=True)
    parser.add_argument(
        "-o", "--output", help="Output file name", default="output.json"
    )

    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = process(json.loads(f.read()))

    pprint(data)

    with open(args.output, "w") as f:
        json.dump(data, f, ensure_ascii=False)
