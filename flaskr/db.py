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
    """Add a file (name + binary content)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (filename, data) VALUES (%s, %s)",
        (filename, data)
    )
    conn.commit()
    conn.close()

def get_all_files():
    """Returns the list of files (ID, name, date)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, uploaded_at FROM files ORDER BY uploaded_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_file_by_id(file_id):
    """Returns a complete file (name + content)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, data FROM files WHERE id = %s", 
        (file_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def delete_file_by_id(file_id):
    """Deletes the entry with the file_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM files where id = %s", 
        (file_id,))
    conn.commit()
    conn.close()

def check_user(username):
    """Retrieve the ID and hashed password for username"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username = %s", 
        (username,))
    user = cursor.fetchone()
    return user


def create_user(username, hashed_password):
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)", 
        (username, hashed_password)
    )
    conn.commit()
    conn.close()
