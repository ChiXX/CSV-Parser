from flask import Blueprint, render_template

authentication: Blueprint = Blueprint("authentication", __name__)


@authentication.route("/login", methods=["GET", "POST"])
def login() -> str:
    return render_template("login.html", text='test')


@authentication.route("/logout")
def logout() -> str:
    return "<h1>logout</h1>"


@authentication.route("/sign-up", methods=["GET", "POST"])
def sing_up() -> str:
    return render_template("signup.html")
