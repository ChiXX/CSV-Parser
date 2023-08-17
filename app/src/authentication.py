from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from app.src.util import validate_existing_user, validate_new_user
from flask_login import login_required, logout_user, current_user


authentication: Blueprint = Blueprint("authentication", __name__)


@authentication.route("/sign-up", methods=["GET", "POST"])
def sign_up() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        new_user_validation = validate_new_user(email, first_name, password1, password2)
        if new_user_validation == "":
            flash("Account created!", category="success")
            return redirect(url_for("homepage.home"))
        flash(new_user_validation, category="error")
    return render_template("signup.html", user=current_user)


@authentication.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user_validation = validate_existing_user(email, password)
        if existing_user_validation == "":
            flash("Logged in successfully!", category="success")
            return redirect(url_for("homepage.home"))
        flash(existing_user_validation, category="error")
    return render_template("login.html", user=current_user)


@authentication.route("/logout")
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("authentication.login"))
