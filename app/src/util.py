import codecs
import csv
import json
import os
from flask import flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.datastructures.file_storage import FileStorage
from .. import db


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
    return content


def has_mandatory_columns(headers: list[str]) -> bool:
    for title in MANDATORY_COLUMNS:
        if title not in headers:
            flash(f"Missing mandatory column: {title}", category="error")
            return False
    return True


@login_required
def validate_file(file: FileStorage) -> list[list[str]] | None:
    if not file:
        return None
    filename = secure_filename(file.filename)
    if not is_allowed_suffix(file.filename):
        flash(f'Invalid file type: {filename.split(".")[1]}', category="error")
    else:
        content = get_csv_content(file)
        if has_mandatory_columns(content[0]):
            from .database import File, Content

            file = File.query.filter_by(filename=filename).first()
            if file:
                return None
            new_file = File(filename=filename, user_id=current_user.id)
            db.session.add(new_file)
            db.session.commit()
            for row in content[1:]:
                [chrom1, start1, end1, chrom2, start2, end2, sample, score] = row
                new_content = Content(
                    chrom1=chrom1,
                    start1=start1,
                    end1=end1,
                    chrom2=chrom2,
                    start2=start2,
                    end2=end2,
                    sample=sample,
                    score=score,
                    file_id=new_file.id,
                )
                db.session.add(new_content)
                db.session.commit()
            return content
    return None
