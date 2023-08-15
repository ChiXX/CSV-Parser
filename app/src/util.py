import codecs
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


def get_file_content(file: FileStorage) -> list[list[str]] | None:
    stream = codecs.iterdecode(file.stream, "utf-8")
    csv_content = try_parse(stream, ",")
    if csv_content:
        return csv_content
    else:
        tsv_content = try_parse(stream, "\t")
        if tsv_content:
            return tsv_content
        else:
            return None


def try_parse(stream, sep=","):
    rows = []
    for row in stream:
        splitted_row = row.strip().split(sep)
        if len(splitted_row) == 1:
            return None
        rows.append(splitted_row)
    return rows


def has_mandatory_columns(headers: list[str]) -> str:
    for title in MANDATORY_COLUMNS:
        if title not in headers:
            return f"Missing mandatory column: {title}"
    return ""


@login_required
def validate_file(file: FileStorage) -> str:
    if not file:
        return ""
    filename = secure_filename(file.filename)
    if not is_allowed_suffix(file.filename):
        return f'Invalid file type: {filename.split(".")[1]}'
    else:
        content = get_file_content(file)
        if not content:
            return "File is not in csv or tsv format"
        validate_headers_msg = has_mandatory_columns(content[0])
        if validate_headers_msg != "":
            return validate_headers_msg

        from .database import File, Content

        file_exists = File.query.filter_by(
            filename=filename, user_id=current_user.id
        ).first()
        if file_exists:
            return f'{filename} is already in the database'
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
        return ""
