import psycopg2
from dotenv import load_dotenv
import os

def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

def add_file(filename, data):
    """Ajoute un fichier (nom + contenu binaire)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (filename, data) VALUES (%s, %s)",
        (filename, data)
    )
    conn.commit()
    conn.close()

def get_all_files():
    """Retourne la liste des fichiers (id, nom, date)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, uploaded_at FROM files ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_file_by_id(file_id):
    """Retourne un fichier complet (nom + contenu)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, data FROM files WHERE id = %s", 
        (file_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_file_by_id(file_id):
    """Supprime l'entrée ayant le file_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM files where id = %s", 
        (file_id,))
    conn.commit()
    conn.close()