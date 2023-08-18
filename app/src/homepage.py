from flask import (
    Blueprint,
    flash,
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

        file_select = file_select_response(file_contents)
        if file_select != "":
            flash(file_select, category="success")

        file_operation = file_operate_response(file_contents)
        if file_operation != "":
            flash(file_operation, category="success")
        file_delete = file_delete_response()

        if file_delete != "":
            flash(file_delete, category="success")
            return redirect(url_for("homepage.home"))

    return render_template(
        "homepage.html", user=current_user, file_contents=file_contents
    )
