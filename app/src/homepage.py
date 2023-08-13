from flask import (
    Blueprint,
    Response,
    render_template,
    request,
)
from flask_login import login_required, current_user
from .util import validate_file


homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    if request.method == "POST":
        file = request.files["file"]
        if file:
            return validate_file(file)

    return render_template("homepage.html", user=current_user)
