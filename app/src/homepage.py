from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.src.util import get_csv_content, has_mandatory_columns, is_allowed_suffix


homepage: Blueprint = Blueprint("homepage", __name__)


@homepage.route("/", methods=["GET", "POST"])
@login_required
def home() -> str | Response:
    if request.method == "POST":
        file = request.files["file"]
        if file:
            print(is_allowed_suffix(file.filename))
            filename = secure_filename(file.filename)
            if not is_allowed_suffix(file.filename):
                print(file.content_length)
                flash(f'Invalid file type: {filename.split(".")[1]}', category="error")
            else:
                content = get_csv_content(file)
                if not has_mandatory_columns(content[0]):
                    flash("Missing mandatory column", category="error")
                else:
                    return redirect(url_for("homepage.home", user=current_user))

        # if file and allowed_file(file.filename):
        #     flash(f'{filename} uploaded!', category='success')

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
