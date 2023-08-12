from flask import Blueprint, render_template
from flask_login import login_required, current_user


homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str:
    return render_template("homepage.html", user=current_user)
