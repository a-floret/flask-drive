from flask import Flask, request, render_template, send_file, abort, redirect, url_for
import io
from db import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    message = None
    if request.method == "POST":
        if "file" not in request.files:
            message = "Aucun fichier reçu"
        else:
            file = request.files["file"]
            if file.filename == "":
                message = "Nom de fichier vide"
            else:
                data = file.read()  # contenu binaire
                add_file(file.filename, data)
                message = f"✅ Fichier {file.filename} enregistré en base !"

    return render_template("upload.html", message=message)

@app.route("/files")
def files():
    files = get_all_files()
    return render_template("files.html", files=files)

@app.route("/download/<int:file_id>")
def download(file_id):
    """Télécharge un fichier stocké en base"""
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
def delete(file_id):
    """Supprime un fichier stocké en base"""
    delete_file_by_id(file_id)
    return redirect(url_for("files"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)