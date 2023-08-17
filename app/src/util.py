import codecs
from flask_login import current_user, login_required, login_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures.file_storage import FileStorage
from .. import db


# File validation

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


def validate_filename(filename: str) -> str:
    if not (
        "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    ):
        return f'Invalid file type: {filename.split(".")[1]}'
    return ""


def parse_fileStorage(file: FileStorage) -> list[list[str]] | None:
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


def parse_fileString(file_string: str) -> str | None:
    lines = file_string.strip().split("\n")
    csv_content = try_parse(lines, ",")
    if csv_content:
        return csv_content
    else:
        tsv_content = try_parse(lines, "\t")
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


def validate_file_content(file_content: list[list[str]] | None) -> str:
    if file_content == None:
        return "File is not in csv or tsv format"
    header_validation = has_mandatory_columns(file_content[0])
    if header_validation != "":
        return header_validation
    return ""


def write_file_to_database(filename, file_content) -> str:
    from .database import File, Content

    existed_file = File.query.filter_by(
        filename=filename, user_id=current_user.id
    ).first()
    if existed_file:
        return f"{filename} is already in the database"
    new_file = File(filename=filename, user_id=current_user.id)
    db.session.add(new_file)
    db.session.commit()
    for row in file_content[1:]:
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


@login_required
def validate_fileStorage(file: FileStorage) -> str:
    if not file:
        return ""
    filename = secure_filename(file.filename)
    filename_validation = validate_filename(filename)
    if filename_validation != "":
        return filename_validation
    file_content = parse_fileStorage(file)
    file_content_validation = validate_file_content(file_content)
    if file_content_validation != "":
        return file_content_validation
    return write_file_to_database(filename, file_content)


@login_required
def validate_fileString(file_string: str, name: str) -> str:
    if file_string == "":
        return "Empty file"
    filename = secure_filename(name)
    filename_validation = validate_filename(filename)
    if filename_validation != "":
        return filename_validation
    file_content = parse_fileString(file_string)
    file_content_validation = validate_file_content(file_content)
    if file_content_validation != "":
        return file_content_validation
    return write_file_to_database(filename, file_content)


# Signup validation


def validate_new_user(email: str, name: str, pwd1: str, pwd2: str) -> str:
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()
    if user:
        return "Email already exists"
    if len(email) < 3:
        return "Email must be greater than 3 characters"
    if len(name) < 2:
        return "First name must be greater than 1 character"
    if pwd1 != pwd2:
        return "Passwords don't match."
    if len(pwd1) < 4:
        return "Password must be at least 7 characters"
    new_user = User(
        email=email,
        first_name=name,
        selected_file="---",
        password=generate_password_hash(pwd1, method="sha256"),
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    return ""


# Login validation


def validate_existing_user(email: str, pwd: str) -> str:
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()
    if not user:
        return "Email does not exist."
    if not check_password_hash(user.password, pwd):
        return "Incorrect password, try again."
    login_user(user, remember=True)
    return ""


# processing home page


class FileData:
    sort_by_options = [
        "---",
        "chrom1",
        "start1",
        "end1",
        "chrom2",
        "start2",
        "end2",
        "sample",
        "score",
    ]
    group_by_options = ["---", "chrom1", "chrom2", "sample"]
    show_top_options = [5, 10, 15, 20]
    sort_by_option = ("---",)
    group_by_option = ("---",)
    show_top_option = (10,)
    is_selected = (False,)

    def __init__(
        self,
        file,
        contents,
    ):
        self.file = file
        self.contents = contents
        self.all_contents = contents

    def set_is_selected(self, is_selected):
        self.is_selected = is_selected

    def write_setting_to_content(self, setting):
        self.sort_by_option = setting.sort_by
        self.group_by_option = setting.group_by
        self.show_top_option = setting.show_top
        self.apply_setting_to_content(
            setting.sort_by, setting.group_by, setting.show_top
        )

    def apply_setting_to_content(
        self,
        sort_by_option="---",
        group_by_option="---",
        show_top_option=10,
    ):
        self.sort_by_option = sort_by_option
        self.group_by_option = group_by_option
        self.show_top_option = int(show_top_option)
        if group_by_option != "---":
            if sort_by_option != "---":
                self.group_and_sort()
            else:
                self.group_and_show_top()
        else:
            if sort_by_option != "---":
                self.sort_and_show_top()
            else:
                self.contents = self.all_contents[: self.show_top_option]

    def sort(self):
        if self.sort_by_option == "chrom1":
            self.all_contents.sort(
                key=lambda x: 23
                if x.chrom1[3:] == "X"
                else 24
                if x.chrom1[3:] == "Y"
                else int(x.chrom1[3:]),
                reverse=False,
            )
        if self.sort_by_option == "chrom2":
            self.all_contents.sort(
                key=lambda x: 23
                if x.chrom2[3:] == "X"
                else 24
                if x.chrom2[3:] == "Y"
                else int(x.chrom2[3:]),
                reverse=False,
            )
        if self.sort_by_option == "sample":
            self.all_contents.sort(
                key=lambda x: int(x.sample[1:]),
                reverse=False,
            )
        if self.sort_by_option == "score":
            self.all_contents.sort(key=lambda x: x.score, reverse=True)
        if self.sort_by_option == "start1":
            self.all_contents.sort(key=lambda x: x.start1, reverse=True)
        if self.sort_by_option == "end1":
            self.all_contents.sort(key=lambda x: x.end1, reverse=True)
        if self.sort_by_option == "start2":
            self.all_contents.sort(key=lambda x: x.start2, reverse=True)
        if self.sort_by_option == "end2":
            self.all_contents.sort(key=lambda x: x.end2, reverse=True)
        if self.sort_by_option == "score":
            self.all_contents.sort(key=lambda x: x.score, reverse=True)

    def sort_and_show_top(self):
        self.sort()
        self.contents = self.all_contents[: self.show_top_option]

    def group_and_show_top(self):
        grouped_contents_dic = {}
        for content in self.all_contents:
            if self.group_by_option == "chrom1":
                grouped_content = grouped_contents_dic.get(content.chrom1)
                if grouped_content == None:
                    grouped_contents_dic[content.chrom1] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "chrom2":
                grouped_content = grouped_contents_dic.get(content.chrom2)
                if grouped_content == None:
                    grouped_contents_dic[content.chrom2] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "sample":
                grouped_content = grouped_contents_dic.get(content.sample)
                if grouped_content == None:
                    grouped_contents_dic[content.sample] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
        self.contents = []
        for grouped_content in grouped_contents_dic.values():
            self.contents = [*self.contents, *grouped_content]

    def group_and_sort(self):
        self.sort()
        self.group_and_show_top()


def read_status_from_database() -> list[FileData]:
    from .database import File, Content, Setting

    all_files = File.query.filter_by(user_id=current_user.id)
    file_contents = []
    for file in all_files:
        all_contents = []
        for validate_content_msg in Content.query.filter_by(file_id=file.id):
            all_contents.append(validate_content_msg)
        file_content = FileData(file, all_contents)
        # TODO Commit system
        setting = Setting.query.filter_by(file_id=file.id).first()
        if setting:
            file_content.write_setting_to_content(setting)
        # TODO Show multiple files
        if current_user.selected_file == file_content.file.filename:
            file_content.set_is_selected(True)
        file_contents.append(file_content)
    return file_contents

def homepage_post_handler() -> str:
    return
