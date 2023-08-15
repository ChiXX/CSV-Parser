from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from .util import validate_file
from .. import db

homepage: Blueprint = Blueprint("homepage", __name__)
api: Blueprint = Blueprint("api", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    from .database import File, Content, Setting

    all_files = File.query.filter_by(user_id=current_user.id)
    file_contents = []
    for file in all_files:
        all_contents = []
        for validate_content_msg in Content.query.filter_by(file_id=file.id):
            all_contents.append(validate_content_msg)
        file_content = FileData(file, all_contents)
        # TODO History system
        setting = Setting.query.filter_by(file_id=file.id).first()
        if setting:
            file_content.write_setting_to_content(setting)
        # TODO Show multiple files
        if current_user.selected_file == file_content.file.filename:
            file_content.set_is_selected(True)
        file_contents.append(file_content)

    if request.method == "POST":
        uploaded_file = request.files["file"]
        validate_content_msg = validate_file(uploaded_file)
        if validate_content_msg != "":
            flash(validate_content_msg, category="error")
        else:
            return redirect(url_for("homepage.home"))
        sortby_dropdown = request.form.get("sortby_dropdown")
        groupby_dropdown = request.form.get("groupby_dropdown")
        show_top = request.form.get("show_top")
        selected_file_name = request.form.get("file_select_button")
        save_setting = request.form.get("save_setting")
        filename_to_delete = request.form.get("delete_button")
        if filename_to_delete:
            file_to_delete = File.query.filter_by(
                user_id=current_user.id, filename=filename_to_delete
            ).first()
            current_user.selected_file = ""
            db.session.delete(file_to_delete)
            db.session.commit()
            return redirect(url_for("homepage.home"))
        if selected_file_name:
            current_user.selected_file = selected_file_name
            db.session.commit()
            for file_content in file_contents:
                if file_content.file.filename == selected_file_name:
                    file_content.set_is_selected(True)
                else:
                    file_content.set_is_selected(False)
        if sortby_dropdown and groupby_dropdown and show_top and save_setting == "":
            for file_content in file_contents:
                if file_content.is_selected:
                    setting = Setting.query.filter_by(
                        file_id=file_content.file.id
                    ).first()
                    if setting:
                        setting.sort_by = sortby_dropdown
                        setting.group_by = groupby_dropdown
                        setting.show_top = show_top
                        file_content.write_setting_to_content(setting)
                        flash("Setting is updated", category="success")
                    else:
                        new_setting = Setting(
                            sort_by=sortby_dropdown,
                            group_by=groupby_dropdown,
                            show_top=show_top,
                            file_id=file_content.file.id,
                        )
                        file_content.write_setting_to_content(new_setting)
                        db.session.add(new_setting)
                        flash("Setting is saved", category="success")
                    db.session.commit()

    return render_template(
        "homepage.html", user=current_user, file_contents=file_contents
    )


@api.route("/api/signup", methods=["POST"])
def sign_up():
    # curl -X POST -H "Content-Type: application/json" -d '{"email": "test@test", "name": "test", "password": "1234"}' http://127.0.0.1:5000/api/signup
    email = request.json.get("email")
    name = request.json.get("name")
    password = request.json.get("password")
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "Email already exists"}), 400
    elif len(email) < 3:
        return jsonify({"error": "Email must be greater than 3 characters."}), 400
    elif len(name) < 2:
        return jsonify({"error": "First name must be greater than 1 character."}), 400
    elif len(password) < 4:
        return jsonify({"error": "Password must be at least 7 characters."}), 400
    else:
        new_user = User(
            email=email,
            first_name=name,
            password=generate_password_hash(password, method="sha256"),
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": "Account created"}), 201


@api.route("/api/upload", methods=["POST"])
def upload_file():
    # curl -X POST -H "Content-Type: multipart/form-data" -F "file=@testfile/example.csv" -F "email=abb@abb" -F "password=1234" 127.0.0.1:5000/api/upload
    email = request.form.get("email")
    password = request.form.get("password")
    from .database import User

    user: User | None = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email does not exist"}), 400
    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 400

    login_user(user, remember=True)
    if "file" not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files["file"]
    validate_content_msg = validate_file(file)

    if validate_content_msg == "":
        return jsonify({"message": "File uploaded successfully"}), 201
    else:
        return jsonify({"error": validate_content_msg}), 400


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

    def __init__(
        self,
        file,
        contents,
        sort_by_option="---",
        group_by_option="---",
        show_top_option=10,
        is_selected=False,
    ):
        self.file = file
        self.contents = contents
        self.all_contents = contents
        self.sort_by_option = sort_by_option
        self.group_by_option = group_by_option
        self.show_top_option = show_top_option
        self.is_selected = is_selected

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
