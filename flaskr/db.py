import sqlite3

DB_NAME = '/database/drive.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initialise la base avec schema.sql"""
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def add_file(filename, data):
    """Ajoute un fichier (nom + contenu binaire)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO files (filename, data) VALUES (?, ?)", (filename, data))
    conn.commit()
    conn.close()

def get_all_files():
    """Retourne la liste des fichiers (id, nom, date)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, uploaded_at FROM files ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_file_by_id(file_id):
    """Retourne un fichier complet (nom + contenu)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, data FROM files WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_file_by_id(file_id):
    """Supprime l'entrée ayant le file_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files where id = ?", (file_id,))
    conn.commit()
    conn.close()