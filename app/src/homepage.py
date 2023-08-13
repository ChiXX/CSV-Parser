from flask import Blueprint, Response, flash, render_template, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.src.util import allowed_file


homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(f'{filename} uploaded!', category='success')
            # return render_template("homepage.html", user=current_user, file=file)
            # new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
            

            # output_file = process_csv(save_location)
            # return send_from_directory('output', output_file)
            # return redirect(url_for("download"))
    return render_template("homepage.html", user=current_user)


# @homepage.route("/upload", methods=["GET", "POST"])
# def upload():
#     if request.method == "POST":
#         file = request.files["file"]
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
#             save_location = os.path.join("input", new_filename)
#             file.save(save_location)

#             # output_file = process_csv(save_location)
#             # return send_from_directory('output', output_file)
#             return redirect(url_for("download"))
#     return render_template("upload.html")
