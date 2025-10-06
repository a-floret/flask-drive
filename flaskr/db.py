import psycopg2
from psycopg2 import pool
import os
import time
from contextlib import contextmanager
from typing import Optional, List, Tuple


class Database:
    """Class for managing the connection to the PostgreSQL database"""
    
    def __init__(self, max_retries=5, retry_delay=2):
        """Initialise connection pool with retry"""
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                self.pool = psycopg2.pool.SimpleConnectionPool(
                    1, 10,  # min et max connections
                    host=os.getenv("POSTGRES_HOST"),
                    port=os.getenv("POSTGRES_PORT"),
                    dbname=os.getenv("POSTGRES_DB"),
                    user=os.getenv("POSTGRES_USER"),
                    password=os.getenv("POSTGRES_PASSWORD")
                )
                print(f"✅ Connected to PostgreSQL at {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}")
                return
            except psycopg2.OperationalError as e:
                last_error = e
                retries += 1
                if retries < max_retries:
                    print(f"⚠️ Failed to connect to PostgreSQL (attempt {retries}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Could not connect to PostgreSQL after {max_retries} attempts")
                    print(f"Error: {last_error}")
                    print(f"Connection details: host={os.getenv('POSTGRES_HOST')}, port={os.getenv('POSTGRES_PORT')}, db={os.getenv('POSTGRES_DB')}")
                    raise
    
    @contextmanager
    def get_connection(self):
        """Context manager to automatically manage connections"""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def close_all(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()


class FileRepository:
    """Repository for managing file operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add(self, filename: str, data: bytes) -> int:
        """Adds a file and returns its ID"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO files (filename, data) VALUES (%s, %s) RETURNING id",
                    (filename, data)
                )
                file_id = cursor.fetchone()[0]
                return file_id
    
    def get_all(self) -> List[Tuple]:
        """Returns a list of all files (ID, name, date)"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, filename, uploaded_at FROM files ORDER BY uploaded_at DESC"
                )
                return cursor.fetchall()
    
    def get_by_id(self, file_id: int) -> Optional[Tuple[str, bytes]]:
        """Returns a complete file by its ID"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT filename, data FROM files WHERE id = %s",
                    (file_id,)
                )
                return cursor.fetchone()
    
    def delete(self, file_id: int) -> bool:
        """Deletes a file, returns True if successful"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM files WHERE id = %s",
                    (file_id,)
                )
                return cursor.rowcount > 0


class UserRepository:
    """Repository for managing user operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_by_username(self, username: str) -> Optional[Tuple[int, str]]:
        """Retrieves a user's ID and password hash"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, password_hash FROM users WHERE username = %s",
                    (username,)
                )
                return cursor.fetchone()
    
    def create(self, username: str, hashed_password: str) -> int:
        """Creates a new user and returns their ID"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, hashed_password)
                )
                user_id = cursor.fetchone()[0]
                return user_id
    
    def exists(self, username: str) -> bool:
        """Check if a user exists"""
        return self.get_by_username(username) is not None


# Global initialisation (singleton pattern)
_db = None
_file_repo = None
_user_repo = None


def init_db():
    """Initialises the database and repositories"""
    global _db, _file_repo, _user_repo
    _db = Database()
    _file_repo = FileRepository(_db)
    _user_repo = UserRepository(_db)


def get_file_repo() -> FileRepository:
    """Returns the FileRepository instance."""
    if _file_repo is None:
        init_db()
    return _file_repo


def get_user_repo() -> UserRepository:
    """Returns the UserRepository instance."""
    if _user_repo is None:
        init_db()
    return _user_repo


def close_db():
    """Close the connection to the database"""
    if _db:
        _db.close_all()