from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from .util import validate_file

homepage: Blueprint = Blueprint("homepage", __name__)


class FileData:
    def __init__(self, file, contents):
        self.file = file
        self.contents = contents


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    print(1)
    from .database import File, Content

    file_contents = []
    files = File.query.filter_by(user_id=current_user.id)
    for f in files:
        contents = []
        for content in Content.query.filter_by(file_id=f.id):
            contents.append(content)
        file_contents.append(FileData(f, contents))
    if request.method == "POST":
        file = request.files["file"]
        content = validate_file(file)
        if content:
            redirect(url_for("homepage.home"))
    return render_template(
        "homepage.html", user=current_user, file_contents=file_contents
    )
