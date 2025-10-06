"""Import modules"""
from flask import Flask, request, render_template, send_file, abort, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from password_validator import PasswordValidator
from datetime import timedelta
from dotenv import load_dotenv
import io
import os
from db import init_db, close_db, get_file_repo, get_user_repo
from auth import login_required

"""Load env variables"""
load_dotenv()

"""App conf"""
app = Flask(__name__, static_url_path="/static/")
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=10)

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

""" Global variables"""
PASSWORD_ERROR_MESSAGE = (
    "⚠️ Weak password ⚠️\n"
    "The password must contain:\n\n"
    "- Between 8 and 25 characters\n"
    "- numbers, letters, characters (no spaces), lowercase, uppercase"
)
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# ============ HOOKS ============
with app.app_context():
    init_db()

# ============ MAIN ROOT ============
@app.route("/")
@login_required
def home():
    """Home Page"""
    return render_template("home.html")

# ============ AUTHENTIFICATION ============

@app.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Field validation
        if not username or not password:
            message = "Username and password are required ❌"
            return render_template("login.html", message_login=message)
        
        # Check credentials
        user_repo = get_user_repo()
        user = user_repo.get_by_username(username)

        if user and check_password_hash(user[1], password):
            session.permanent = True
            session["user_id"] = user[0]
            session["username"] = username
            flash(f"Welcome back, {username}! 👋", "success")
            return redirect(url_for("home"))
        else:
            message = "Incorrect credentials ❌"

    return render_template("login.html", message_login=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration for User"""
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_c = request.form.get("password_c", "")

        #Validate username
        if not username:
            message = "Username is required ❌"
            return render_template("register.html", message_register=message)

        # Check if user alrady exist
        user_repo = get_user_repo()
        if user_repo.exists(username):
            message = "Username already taken ❌"
            return render_template("register.html", message_register=message, username=username)
        
        # Check password complexity
        if not schema.validate(password):
            return render_template("register.html", message_register=PASSWORD_ERROR_MESSAGE, username=username)

        # Check password confirmation
        if password != password_c:
            message = "Passwords are not identical ❌"
            return render_template("register.html", message_register=message, username=username)

        # Create user
        try:
            hashed_password = generate_password_hash(password)
            user_repo.create(username, hashed_password)
            flash("Account successfully created ✅", "success")
            return redirect(url_for("login"))
        except Exception as e:
            app.logger.error(f"Error creating user: {e}")
            message = "An error occurred during registration ❌"
            return render_template("register.html", message_register=message, username=username)

    return render_template("register.html", message_register=message)

@app.route("/logout", methods=["POST"])
def logout():
    """Logout"""
    username = session.get("username", "User")
    session.clear()
    flash(f"Goodbye {username}! See you soon 👋", "info")
    return redirect(url_for("login"))

# ============ FILE MANAGEMENT ============
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Files upload"""
    message = None
    message_type = None

    if request.method == "POST":
        # Checking for the presence of the file
        if "file" not in request.files:
            message = "No files received ❌"
            message_type = "error"
        else:
            file = request.files["file"]
            
            if file.filename == "":
                message = "Empty file name ❌"
                message_type = "error"
            else:
                # File size validation (optional, e.g. 16MB max)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)

                if file_size > MAX_FILE_SIZE:
                    message = f"File too large (max 16MB) ❌"
                    message_type = "error"
                else:
                    try:
                        data = file.read()
                        file_repo = get_file_repo()
                        file_id = file_repo.add(file.filename, data)
                        message = f"✅ File '{file.filename}' saved in database (ID: {file_id})!"
                        message_type = "success"
                    except Exception as e:
                        app.logger.error(f"Error uploading file: {e}")
                        message = "An error occurred while uploading the file ❌"
                        message_type = "error"

    return render_template("upload.html", message=message, message_type=message_type)



@app.route("/files")
@login_required
def files():
    """List of files"""
    try:
        file_repo = get_file_repo()
        files_list = file_repo.get_all()
        return render_template("files.html", files=files_list)
    except Exception as e:
        app.logger.error(f"Error fetching files: {e}")
        flash("Error loading files ❌", "error")
        return render_template("files.html", files=[])

@app.route("/download/<int:file_id>")
@login_required
def download(file_id):
    """Download file"""
    try:
        file_repo = get_file_repo()
        row = file_repo.get_by_id(file_id)
        
        if row is None:
            flash("File not found ❌", "error")
            abort(404)
        
        filename, data = row
        return send_file(
            io.BytesIO(data),
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        app.logger.error(f"Error downloading file {file_id}: {e}")
        flash("Error downloading file ❌", "error")
        return redirect(url_for("files"))

@app.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    """Delete a file"""
    try:
        file_repo = get_file_repo()
        success = file_repo.delete(file_id)
        
        if success:
            flash("File deleted successfully ✅", "success")
        else:
            flash("File not found ❌", "error")
    except Exception as e:
        app.logger.error(f"Error deleting file {file_id}: {e}")
        flash("Error deleting file ❌", "error")
    
    return redirect(url_for("files"))


# ============ ERROR MANAGEMENT ============

@app.errorhandler(404)
def not_found(error):
    """Page 404"""
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Page 500"""
    app.logger.error(f"Internal error: {error}")
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)