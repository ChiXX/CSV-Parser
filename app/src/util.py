import csv
import os
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

def process_csv(filename: str)-> str:
    product_types = defaultdict(Decimal)

    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hypen_idx = row['product'].replace('"', '').split().index('-')
                product_type =  ' '.join(row['product'].split()[:hypen_idx])
                product_types[product_type] += Decimal(row['price'][1:])
            except ValueError:
                product_types[row['product'].replace('"', '')] += Decimal(row['price'][1:])

    output_file = f'product_types_{str(datetime.now())}.csv'
    with open(os.path.join('output', output_file), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['product_type', 'price'])

        for product_type, price in product_types.items():
            writer.writerow([product_type, price])

    return output_file

ALLOWED_EXTENSIONS: set[str] = set(["csv"])

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS