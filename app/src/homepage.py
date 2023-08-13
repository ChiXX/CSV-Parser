from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from .util import validate_file

homepage: Blueprint = Blueprint("homepage", __name__)


class FileData:
    _contents = []

    def __init__(self, file, headers, contents, by=""):
        self.file = file
        self.headers = headers
        self.contents = contents
        self.by = by
        self._contents = contents

    def sort_by(self, by):
        self.by = by
        if by == "chrom1":
            self._contents.sort(
                key=lambda x: float('inf') if x.chrom1[3:] == "X" else int(x.chrom1[3:]),
                reverse=False,
            )
        if by == "chrom2":
            self._contents.sort(
                key=lambda x: float('inf') if x.chrom2[3:] == "X" else int(x.chrom2[3:]),
                reverse=False,
            )
        if by == "sample":
            self._contents.sort(
                key=lambda x: int(x.sample[1:]),
                reverse=False,
            )
        if by == "score":
            self._contents.sort(key=lambda x: x.score, reverse=True)
        if by == "start1":
            self._contents.sort(key=lambda x: x.start1, reverse=True)
        if by == "end1":
            self._contents.sort(key=lambda x: x.end1, reverse=True)
        if by == "start2":
            self._contents.sort(key=lambda x: x.start2, reverse=True)
        if by == "end2":
            self._contents.sort(key=lambda x: x.end2, reverse=True)
        if by == "score":
            self._contents.sort(key=lambda x: x.score, reverse=True)

    def show_top(self, cols=10):
        self.contents = self._contents[:cols]


SHOW_TOP = 10


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    from .database import File, Content

    headers = filter(lambda h: "id" not in h, Content.__table__.columns.keys())
    file_contents = []
    files = File.query.filter_by(user_id=current_user.id)

    for f in files:
        contents = []
        for content in Content.query.filter_by(file_id=f.id):
            contents.append(content)
        file_content = FileData(f, headers, contents)
        file_content.sort_by("chrom1")
        file_content.show_top(SHOW_TOP)
        file_contents.append(file_content)
    if request.method == "POST":
        file = request.files["file"]
        content = validate_file(file)
        sortby_dropdown = request.form.get("sortby_dropdown")

        if content:
            return redirect(url_for("homepage.home"))
        if sortby_dropdown:
            for f in file_contents:
                f.sort_by(sortby_dropdown)
                f.show_top(SHOW_TOP)
            return render_template(
                "homepage.html", user=current_user, file_contents=file_contents
            )

    return render_template(
        "homepage.html", user=current_user, file_contents=file_contents
    )
