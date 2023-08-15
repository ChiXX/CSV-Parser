from sqlalchemy.sql import func
from .. import db
from flask_login import UserMixin


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chrom1 = db.Column(db.String(150), nullable=False)
    start1 = db.Column(db.Integer, nullable=False)
    end1 = db.Column(db.Integer, nullable=False)
    chrom2 = db.Column(db.String(150), nullable=False)
    start2 = db.Column(db.Integer, nullable=False)
    end2 = db.Column(db.Integer, nullable=False)
    sample = db.Column(db.String(150), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"))


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sort_by = db.Column(db.String(150), nullable=False)
    group_by = db.Column(db.String(150), nullable=False)
    show_top = db.Column(db.Integer, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"))


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    contents = db.relationship("Content")
    Settings = db.relationship("Setting")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    selected_file = db.Column(db.String(150))
    files = db.relationship("File")
