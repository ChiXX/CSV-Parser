import codecs
from flask import request
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


def parse_fileString(file_string: str) -> list[list[str]] | None:
    lines = file_string.strip().split("\n")
    csv_content = try_parse(lines, ",")
    if csv_content is not None:
        return csv_content
    else:
        tsv_content = try_parse(lines, "\t")
        return tsv_content


def try_parse(stream, sep=",") -> list[list[str]] | None:
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
    if file_content is None:
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
    if not file or file.filename is None:
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


def validate_new_user(
    email: str | None, name: str | None, pwd1: str | None, pwd2: str | None
) -> str:
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()

    if user:
        return "Email already exists"
    if email is None or len(email) < 3:
        return "Email must be greater than 3 characters"
    if name is None or len(name) < 2:
        return "First name must be greater than 1 character"
    if pwd1 is None or len(pwd1) < 4:
        return "Password must be at least 7 characters"
    if pwd1 != pwd2:
        return "Passwords don't match."
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


def validate_existing_user(email: str | None, pwd: str | None) -> str:
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()
    if not user:
        return "Email does not exist."
    if pwd is None or not check_password_hash(user.password, pwd):
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
    sort_by_option = "---"
    group_by_option = "---"
    show_top_option = 10
    is_selected = False

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
                if grouped_content is None:
                    grouped_contents_dic[content.chrom1] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "chrom2":
                grouped_content = grouped_contents_dic.get(content.chrom2)
                if grouped_content is None:
                    grouped_contents_dic[content.chrom2] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "sample":
                grouped_content = grouped_contents_dic.get(content.sample)
                if grouped_content is None:
                    grouped_contents_dic[content.sample] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
        self.contents = []
        for grouped_content in grouped_contents_dic.values():
            self.contents = [*self.contents, *grouped_content]

    def group_and_sort(self) -> None:
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


def file_post_response() -> str:
    uploaded_file = request.files["file"]
    file_validation = validate_fileStorage(uploaded_file)
    return file_validation


def file_delete_response() -> str:
    from .database import File

    filename_to_delete = request.form.get("delete_button")
    if filename_to_delete:
        file_to_delete = File.query.filter_by(
            user_id=current_user.id, filename=filename_to_delete
        ).first()
        current_user.selected_file = ""
        db.session.delete(file_to_delete)
        db.session.commit()
        return f"{filename_to_delete} deleted successfully"
    return ""


def file_select_response(file_contents: list[FileData]) -> str:
    selected_file_name = request.form.get("file_select_button")
    if selected_file_name:
        current_user.selected_file = selected_file_name
        db.session.commit()
        for file_content in file_contents:
            if file_content.file.filename == selected_file_name:
                file_content.set_is_selected(True)
            else:
                file_content.set_is_selected(False)
        return f"{selected_file_name} is selected"
    return ""


def file_operate_response(file_contents: list[FileData]) -> str:
    from .database import Setting

    sortby_dropdown = request.form.get("sortby_dropdown")
    groupby_dropdown = request.form.get("groupby_dropdown")
    show_top = request.form.get("show_top")
    save_setting = request.form.get("save_setting")
    status = ""
    if sortby_dropdown and groupby_dropdown and show_top and save_setting == "":
        for file_content in file_contents:
            if file_content.is_selected:
                setting = Setting.query.filter_by(file_id=file_content.file.id).first()
                if setting:
                    setting.sort_by = sortby_dropdown
                    setting.group_by = groupby_dropdown
                    setting.show_top = show_top
                    file_content.write_setting_to_content(setting)
                    status = "Setting is updated"
                else:
                    new_setting = Setting(
                        sort_by=sortby_dropdown,
                        group_by=groupby_dropdown,
                        show_top=show_top,
                        file_id=file_content.file.id,
                    )
                    file_content.write_setting_to_content(new_setting)
                    db.session.add(new_setting)
                    status = "Setting is saved"
                db.session.commit()
    return status
