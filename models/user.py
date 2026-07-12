from database.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

    @classmethod
    def get_by_id(cls, user_id):
        conn = get_db_connection()
        row = conn.execute("SELECT id, username, role FROM users WHERE id = ?;", (user_id,)).fetchone()
        conn.close()
        if row:
            return cls(row['id'], row['username'], row['role'])
        return None

    @classmethod
    def get_by_username(cls, username):
        conn = get_db_connection()
        row = conn.execute("SELECT id, username, role FROM users WHERE username = ?;", (username,)).fetchone()
        conn.close()
        if row:
            return cls(row['id'], row['username'], row['role'])
        return None

    @classmethod
    def verify_login(cls, username, password):
        conn = get_db_connection()
        row = conn.execute("SELECT id, username, password, role FROM users WHERE username = ?;", (username,)).fetchone()
        conn.close()
        if row and check_password_hash(row['password'], password):
            return cls(row['id'], row['username'], row['role'])
        return None

    @classmethod
    def create_user(cls, username, password, role):
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?);",
                (username, hashed_password, role)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def get_all(cls):
        conn = get_db_connection()
        rows = conn.execute("SELECT id, username, role FROM users;").fetchall()
        conn.close()
        return [cls(r['id'], r['username'], r['role']) for r in rows]
