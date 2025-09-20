from flask import Flask, request, render_template, send_from_directory
import os

app = Flask(__name__)

FILE_FOLDER = "/database"
os.makedirs(FILE_FOLDER, exist_ok=True)

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
                filepath = os.path.join(FILE_FOLDER, file.filename)
                file.save(filepath)
                message = f"✅ Fichier {file.filename} uploadé avec succès !"

    return render_template("upload.html", message=message)

@app.route("/files")
def files():
    filenames = os.listdir(FILE_FOLDER)
    return render_template('files.html', files=filenames)

@app.route('/files/<path:filename>')
def file(filename):
    return send_from_directory(
        os.path.abspath(FILE_FOLDER),
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
