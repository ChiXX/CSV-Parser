from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from werkzeug import Response
from .util import (
    file_delete_response,
    file_operate_response,
    file_post_response,
    file_select_response,
    read_status_from_database,
    validate_existing_user,
    validate_fileString,
    validate_new_user,
)

homepage: Blueprint = Blueprint("homepage", __name__)
api: Blueprint = Blueprint("api", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    file_contents = read_status_from_database()

    if request.method == "POST":
        file_upload = file_post_response()
        if file_upload != "":
            flash(file_upload, category="error")
            return redirect(url_for("homepage.home"))

        file_delete = file_delete_response()
        if file_delete != "":
            flash(file_delete, category="success")
            return redirect(url_for("homepage.home"))

        file_select = file_select_response(file_contents)
        if file_select != "":
            flash(file_select, category="success")
            return redirect(url_for("homepage.home"))

        file_operation = file_operate_response(file_contents)
        if file_operation != "":
            flash(file_operation, category="success")
            return redirect(url_for("homepage.home"))

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
