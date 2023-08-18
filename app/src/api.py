from flask import (
    Blueprint,
    jsonify,
    request,
)
from .util import (
    validate_existing_user,
    validate_fileString,
    validate_new_user,
)

api: Blueprint = Blueprint("api", __name__)


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


# curl.exe -H "Content-Type: text/csv" -H "filename: example.csv" --data-binary "@testfile/example.csv" -u aaa@aaa:1234 127.0.0.1:5000/api/upload
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
