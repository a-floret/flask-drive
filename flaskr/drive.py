"""Import modules"""
from flask import Flask, request, render_template, send_file, abort, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from password_validator import PasswordValidator
from datetime import timedelta
import io
import os
from db import *
from auth import *

""" Create passsword schema"""
schema = PasswordValidator()

schema\
.min(8)\
.max(25)\
.has().uppercase()\
.has().lowercase()\
.has().digits()\
.has().letters()\
.has().no().spaces()\

"""Start application"""
app = Flask(__name__, static_url_path="/static/")
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=10) 

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        fetch = check_user(username)

        if fetch and check_password_hash(fetch[1], password):  
            session["user_id"] = fetch[0]
            return redirect(url_for("home"))  
        else:
            message = "Incorrect credentials ❌"

    return render_template("login.html", message_login=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        username  = request.form["username"]
        password  = request.form["password"]
        password_c = request.form["password_c"]

        if check_user(username):
            message = "Username already taken ❌"
            return render_template("register.html", message_register=message, username=username)
        

        if not schema.validate(password):
            message = (
                "⚠️ Weak password  ⚠️\n"
                "The password must contain:\n\n"
                "- Between 8 and 25 characters\n"
                "- numbers, letters, characters (no spaces), lowercase, uppercase"
            )
            return render_template("register.html", message_register= message, username=username)

        if password == password_c:
            create_user(username, generate_password_hash(password))
            flash("Account successfully created  ✅")
            return redirect(url_for("login"))
        else:
            message = "Passwords are not identical  ❌"
            return render_template("register.html", message_register= message, username=username) 

    return render_template("register.html", message_register=message)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    message = None
    if request.method == "POST":
        if "file" not in request.files:
            message = "No files received"
        else:
            file = request.files["file"]
            if file.filename == "":
                message = "Empty file name"
            else:
                data = file.read()
                add_file(file.filename, data)
                message = f"✅ File {file.filename} saved in database  !"

    return render_template("upload.html", message=message)

@app.route("/files")
@login_required
def files():
    files = get_all_files()
    return render_template("files.html", files=files)

@app.route("/download/<int:file_id>")
@login_required
def download(file_id):
    """Download a file stored in the database"""
    row = get_file_by_id(file_id)
    if row is None:
        abort(404)
    filename, data = row
    return send_file(
        io.BytesIO(data),
        download_name=filename,
        as_attachment=True
    )

@app.route("/delete/<int:file_id>")
@login_required
def delete(file_id):
    """Deletes a file stored in the database"""
    delete_file_by_id(file_id)
    return redirect(url_for("files"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)