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
from flask_login import login_required, current_user
from .util import (
    read_status_from_database,
    validate_existing_user,
    validate_fileStorage,
    validate_fileString,
    validate_new_user,
)
from .. import db

homepage: Blueprint = Blueprint("homepage", __name__)
api: Blueprint = Blueprint("api", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    from .database import File, Setting

    file_contents = read_status_from_database()

    if request.method == "POST":
        uploaded_file = request.files["file"]
        file_validation = validate_fileStorage(uploaded_file)
        if file_validation != "":
            flash(file_validation, category="error")
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


# curl -X POST -H "Content-Type: application/json" -d '{"email": "test@test", "name": "test", "password": "1234"}' http://127.0.0.1:5000/api/signup
@api.route("/api/signup", methods=["POST"])
def sign_up():
    email = request.json.get("email")
    name = request.json.get("name")
    password = request.json.get("password")
    new_user_validation = validate_new_user(email, name, password, password)
    if new_user_validation != "":
        return jsonify({"error": new_user_validation}), 400
    return jsonify({"success": "Account created"}), 201


# curl.exe -H "Content-Type: text/csv" -H "filename: example.csv" --data-binary "@testfile/example.csv" -u aaa@aaa:1234 127.0.0.1:5000/upload
@api.route("/api/upload", methods=["POST"])
def upload_file():
    auth = request.authorization
    existing_user_validation = validate_existing_user(auth.username, auth.password)
    if existing_user_validation != "":
        return jsonify({"error": existing_user_validation}), 400

    file_string = request.data.decode("utf-8")
    filename = request.headers.get("filename")
    file_validation = validate_fileString(file_string, filename)
    if file_validation != "":
        return jsonify({"error": file_validation}), 400
    return jsonify({"message": "File uploaded successfully"}), 201
