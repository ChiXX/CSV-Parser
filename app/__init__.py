from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db: SQLAlchemy = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "J7FhNA8hx0qcDFDBDITpcldGIx8QXKlm"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Maximum file size: 16 MB
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .src.homepage import homepage, api
    from .src.authentication import authentication

    app.register_blueprint(homepage, url_prefix="/")
    app.register_blueprint(api, url_prefix="/")
    app.register_blueprint(authentication, url_prefix="/")

    with app.app_context():
        db.create_all()

    from .src.database import User

    login_manager = LoginManager()
    login_manager.login_view = "authentication.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
