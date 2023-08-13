import codecs
import csv
import os
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from werkzeug.datastructures.file_storage import FileStorage


def process_csv(filename: str) -> str:
    product_types = defaultdict(Decimal)

    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hypen_idx = row["product"].replace('"', "").split().index("-")
                product_type = " ".join(row["product"].split()[:hypen_idx])
                product_types[product_type] += Decimal(row["price"][1:])
            except ValueError:
                product_types[row["product"].replace('"', "")] += Decimal(
                    row["price"][1:]
                )

    output_file = f"product_types_{str(datetime.now())}.csv"
    with open(os.path.join("output", output_file), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["product_type", "price"])

        for product_type, price in product_types.items():
            writer.writerow([product_type, price])

    return output_file


ALLOWED_EXTENSIONS: set[str] = set(["csv", "tsv"])
MANDATORY_COLUMNS: list[str] = [
    "chrom1",
    "start1",
    "end1",
    "chrom2",
    "end2",
    "sample",
    "score",
]


def is_allowed_suffix(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_csv_content(file: FileStorage) -> list[list[str]]:
    stream = codecs.iterdecode(file.stream, "utf-8")
    rows = csv.reader(stream, dialect=csv.excel)
    content = []
    for row in rows:
        content.append(row) 
    return row

def has_mandatory_columns(headers: list[str]) -> bool:
    for title in MANDATORY_COLUMNS:
        if title not in headers:
            return False
    return True
