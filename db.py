import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash


def get_conn():
    """Return a new psycopg2 connection using env vars or sensible defaults."""
    config = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "5432")),
        "dbname": os.environ.get("DB_NAME", "water_management_database"),
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ.get("DB_PASSWORD", "12345"),
    }
    return psycopg2.connect(**config)


def verify_user(email: str, password: str):
    """Verify credentials. Returns dict with `id` and `name` when OK, else None."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, name, password FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                if not row:
                    return None
                stored = row["password"]
                # Support hashed passwords and plain-text (legacy) for convenience
                if check_password_hash(stored, password) or stored == password:
                    return {"id": row["id"], "name": row["name"]}
                return None
    except Exception as e:
        print("DB verify_user error:", e)
        return None


def create_user(name: str, email: str, password: str):
    """Create a new user. Returns True on success, False if user exists or on error."""
    hashed = generate_password_hash(password)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    return False
                cur.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
                    (name, email, hashed),
                )
                new_id = cur.fetchone()[0]
                conn.commit()
                return True
    except Exception as e:
        print("DB create_user error:", e)
        return False
