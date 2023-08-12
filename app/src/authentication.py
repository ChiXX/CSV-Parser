from flask import Blueprint, render_template, request, flash

authentication: Blueprint = Blueprint("authentication", __name__)


@authentication.route("/login", methods=["GET", "POST"])
def login() -> str:
    return render_template("login.html", text="test")


@authentication.route("/logout")
def logout() -> str:
    return "<h1>logout</h1>"


@authentication.route("/sign-up", methods=["GET", "POST"])
def sing_up() -> str:
    if request.method == "POST":
        email: str = request.form.get("email")
        first_name: str = request.form.get("firstName")
        password1: str = request.form.get("password1")
        password2: str = request.form.get("password2")

        # user = User.query.filter_by(email=email).first()
        if False:
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("Passwords don't match.", category="error")
        elif len(password1) < 4:
            flash("Password must be at least 4 characters.", category="error")
        else:
            pass
    return render_template("signup.html")
