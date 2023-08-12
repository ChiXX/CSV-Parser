from flask import Flask

data = {"a": 0, "b": [[1, 2], [3, 4]], "c": 5}


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "J7FhNA8hx0qcDFDBDITpcldGIx8QXKlm"

    from .src.homepage import homepage
    from .src.authentication import authentication

    app.register_blueprint(homepage, url_prefix="/")
    app.register_blueprint(authentication, url_prefix="/")

    return app
