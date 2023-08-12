from flask import Blueprint, render_template

homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
def home() -> str:
    return render_template("homepage.html")
