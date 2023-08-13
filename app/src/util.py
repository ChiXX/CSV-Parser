import codecs
import csv
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures.file_storage import FileStorage
from flask import Response, redirect, url_for, flash

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
        print(row)
        content.append(row)
    return content


def has_mandatory_columns(headers: list[str]) -> bool:
    for title in MANDATORY_COLUMNS:
        if title not in headers:
            flash(f"Missing mandatory column: {title}", category="error")
            return False
    return True


def validate_file(file: FileStorage) -> Response:
    filename = secure_filename(file.filename)
    if not is_allowed_suffix(file.filename):
        flash(f'Invalid file type: {filename.split(".")[1]}', category="error")
    else:
        content = get_csv_content(file)
        if not has_mandatory_columns(content[0]):
            pass
        else:
            return redirect(url_for("homepage.home", user=current_user))
    return redirect(url_for("homepage.home", user=current_user))
