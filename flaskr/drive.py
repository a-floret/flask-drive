from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Dossier de stockage des fichiers
FILE_FOLDER = "/database"
os.makedirs(FILE_FOLDER, exist_ok=True)

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

#@app.route("/files")
#def files():
#    return "List all present files"

#@app.route("/downloads")
#def files():
#    return "Downloads files"

@app.route("/")
def home():
    #return redirect(url_for('foo'))
    return "Hello from Flask in a container!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
