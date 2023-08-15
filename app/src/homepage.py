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
from .. import db

homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    from .database import File, Content, Setting

    file_contents = []
    file = File.query.filter_by(user_id=current_user.id).first()

    if file:
        all_contents = []
        for content in Content.query.filter_by(file_id=file.id):
            all_contents.append(content)
        file_content = FileData(file, all_contents)
        setting = Setting.query.filter_by(file_id=file.id).first()
        if setting:
            file_content.write_setting_to_content(setting)
        file_contents.append(file_content)
    if request.method == "POST":
        file = request.files["file"]
        content = validate_file(file)
        sortby_dropdown = request.form.get("sortby_dropdown")
        groupby_dropdown = request.form.get("groupby_dropdown")
        show_top = request.form.get("show_top")
        save_setting = request.form.get("save_setting")
        if content:
            return redirect(url_for("homepage.home"))
        if sortby_dropdown and groupby_dropdown and show_top:
            for file_content in file_contents:
                file_content.apply_setting_to_content(
                    sortby_dropdown, groupby_dropdown, show_top
                )
            if save_setting:
                for file_content in file_contents:
                    setting = Setting.query.filter_by(
                        file_id=file_content.file.id
                    ).first()
                    if setting:
                        setting.sort_by = sortby_dropdown
                        setting.group_by = groupby_dropdown
                        setting.show_top = show_top
                    else:
                        new_setting = Setting(
                            sort_by=sortby_dropdown,
                            group_by=groupby_dropdown,
                            show_top=show_top,
                            file_id=file_content.file.id,
                        )
                        db.session.add(new_setting)
                    db.session.commit()
    return render_template(
        "homepage.html", user=current_user, file_contents=file_contents
    )


class FileData:
    sort_by_options = [
        "---",
        "chrom1",
        "start1",
        "end1",
        "chrom2",
        "start2",
        "end2",
        "sample",
        "score",
    ]
    group_by_options = ["---", "chrom1", "chrom2", "sample"]
    show_top_options = [5, 10, 15, 20]

    def __init__(
        self,
        file,
        contents,
        sort_by_option="---",
        group_by_option="---",
        show_top_option=10,
    ):
        self.file = file
        self.contents = contents
        self.all_contents = contents
        self.sort_by_option = sort_by_option
        self.group_by_option = group_by_option
        self.show_top_option = show_top_option

    def write_setting_to_content(self, setting):
        self.sort_by_option = setting.sort_by
        self.group_by_option = setting.group_by
        self.show_top_option = setting.show_top
        self.apply_setting_to_content(
            setting.sort_by, setting.group_by, setting.show_top
        )

    def apply_setting_to_content(
        self,
        sort_by_option="---",
        group_by_option="---",
        show_top_option=10,
    ):
        self.sort_by_option = sort_by_option
        self.group_by_option = group_by_option
        self.show_top_option = int(show_top_option)
        if group_by_option != "---":
            if sort_by_option != "---":
                self.group_and_sort()
            else:
                self.group_and_show_top()
        else:
            if sort_by_option != "---":
                self.sort_and_show_top()
            else:
                self.contents = self.all_contents[: self.show_top_option]

    def sort(self):
        if self.sort_by_option == "chrom1":
            self.all_contents.sort(
                key=lambda x: 23
                if x.chrom1[3:] == "X"
                else 24
                if x.chrom1[3:] == "Y"
                else int(x.chrom1[3:]),
                reverse=False,
            )
        if self.sort_by_option == "chrom2":
            self.all_contents.sort(
                key=lambda x: 23
                if x.chrom2[3:] == "X"
                else 24
                if x.chrom2[3:] == "Y"
                else int(x.chrom2[3:]),
                reverse=False,
            )
        if self.sort_by_option == "sample":
            self.all_contents.sort(
                key=lambda x: int(x.sample[1:]),
                reverse=False,
            )
        if self.sort_by_option == "score":
            self.all_contents.sort(key=lambda x: x.score, reverse=True)
        if self.sort_by_option == "start1":
            self.all_contents.sort(key=lambda x: x.start1, reverse=True)
        if self.sort_by_option == "end1":
            self.all_contents.sort(key=lambda x: x.end1, reverse=True)
        if self.sort_by_option == "start2":
            self.all_contents.sort(key=lambda x: x.start2, reverse=True)
        if self.sort_by_option == "end2":
            self.all_contents.sort(key=lambda x: x.end2, reverse=True)
        if self.sort_by_option == "score":
            self.all_contents.sort(key=lambda x: x.score, reverse=True)

    def sort_and_show_top(self):
        self.sort()
        self.contents = self.all_contents[: self.show_top_option]

    def group_and_show_top(self):
        grouped_contents_dic = {}
        for content in self.all_contents:
            if self.group_by_option == "chrom1":
                grouped_content = grouped_contents_dic.get(content.chrom1)
                if grouped_content == None:
                    grouped_contents_dic[content.chrom1] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "chrom2":
                grouped_content = grouped_contents_dic.get(content.chrom2)
                if grouped_content == None:
                    grouped_contents_dic[content.chrom2] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
            if self.group_by_option == "sample":
                grouped_content = grouped_contents_dic.get(content.sample)
                if grouped_content == None:
                    grouped_contents_dic[content.sample] = []
                elif self.show_top_option >= len(grouped_content):
                    grouped_content.append(content)
        self.contents = []
        for grouped_content in grouped_contents_dic.values():
            self.contents = [*self.contents, *grouped_content]

    def group_and_sort(self):
        self.sort()
        self.group_and_show_top()
