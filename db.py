import os
import uuid
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


def ensure_schema():
    """Create the required tables and default admin account if missing."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id VARCHAR(50) PRIMARY KEY,
                        admin_name VARCHAR(100) NOT NULL,
                        admin_address TEXT,
                        phone_number VARCHAR(15) NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        username VARCHAR(50) UNIQUE,
                        password VARCHAR(255) NOT NULL
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS water_schedules (
                        schedule_id VARCHAR(50) PRIMARY KEY,
                        location VARCHAR(255) NOT NULL,
                        delivery_time VARCHAR(255) NOT NULL,
                        latitude VARCHAR(50),
                        longitude VARCHAR(50)
                    )
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS latitude VARCHAR(50)
                    """
                )
                cur.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN IF NOT EXISTS longitude VARCHAR(50)
                    """
                )
                cur.execute(
                    "SELECT admin_id FROM admins WHERE username = %s",
                    ("admin",),
                )
                if not cur.fetchone():
                    admin_id = f"ADMIN-{uuid.uuid4().hex[:8].upper()}"
                    password_hash = generate_password_hash("admin")
                    cur.execute(
                        "INSERT INTO admins (admin_id, admin_name, admin_address, phone_number, email, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (admin_id, "admin", "", "0712345678", "admin@email.com", "admin", password_hash),
                    )
                conn.commit()
    except Exception as e:
        print("DB ensure_schema error:", e)


ensure_schema()


def verify_user(email: str, password: str):
    """Verify credentials. Returns dict with `id` and `name` when OK, else None."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id, user_name, password FROM users WHERE email = %s OR username = %s",
                    (email, email),
                )
                row = cur.fetchone()
                if not row:
                    return None
                stored = row["password"]
                if check_password_hash(stored, password) or stored == password:
                    return {"id": row["user_id"], "name": row["user_name"]}
                return None
    except Exception as e:
        print("DB verify_user error:", e)
        return None


def create_user(name: str, email: str, password: str, address: str = "", latitude: str = "", longitude: str = ""):
    """Create a new user. Returns True on success, False if user exists or on error."""
    hashed = generate_password_hash(password)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT user_id FROM users WHERE email = %s OR username = %s",
                    (email, email),
                )
                if cur.fetchone():
                    return False
                username = email.split("@")[0]
                user_id = f"USER-{uuid.uuid4().hex[:8].upper()}"
                cur.execute(
                    "INSERT INTO users (user_id, user_name, user_address, phone_number, fee_balance, email, username, password, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (user_id, name, address, "", 0.00, email, username, hashed, latitude, longitude),
                )
                conn.commit()
                return True
    except Exception as e:
        print("DB create_user error:", e)
        return False


def verify_admin(email: str, password: str):
    """Verify admin credentials. Returns admin data dict when valid."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT admin_id, admin_name, password FROM admins WHERE email = %s OR username = %s",
                    (email, email),
                )
                row = cur.fetchone()
                if not row:
                    return None
                stored = row["password"]
                if check_password_hash(stored, password) or stored == password:
                    return {"id": row["admin_id"], "name": row["admin_name"]}
                return None
    except Exception as e:
        print("DB verify_admin error:", e)
        return None


def get_all_users():
    """Return a list of all registered users."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id, user_name, email, username, phone_number, fee_balance FROM users ORDER BY user_name"
                )
                return cur.fetchall()
    except Exception as e:
        print("DB get_all_users error:", e)
        return []


def create_schedule(location: str, delivery_time: str, latitude: str = "", longitude: str = ""):
    """Create a new water delivery schedule entry."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                schedule_id = f"SCH-{uuid.uuid4().hex[:8].upper()}"
                cur.execute(
                    "INSERT INTO water_schedules (schedule_id, location, delivery_time, latitude, longitude) VALUES (%s, %s, %s, %s, %s)",
                    (schedule_id, location, delivery_time, latitude, longitude),
                )
                conn.commit()
                return True
    except Exception as e:
        print("DB create_schedule error:", e)
        return False


def get_all_schedules():
    """Return all available schedules ordered by newest entries first."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT schedule_id, location, delivery_time, latitude, longitude FROM water_schedules ORDER BY schedule_id DESC"
                )
                return cur.fetchall()
    except Exception as e:
        print("DB get_all_schedules error:", e)
        return []


def get_schedules_for_location(location: str):
    """Return schedules for a specific area, with fallback to all schedules if none match."""
    if not location:
        return get_all_schedules()
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT schedule_id, location, delivery_time, latitude, longitude FROM water_schedules WHERE LOWER(location) = LOWER(%s) ORDER BY schedule_id DESC",
                    (location,),
                )
                rows = cur.fetchall()
                if rows:
                    return rows
                return get_all_schedules()
    except Exception as e:
        print("DB get_schedules_for_location error:", e)
        return get_all_schedules()


def get_user_profile(user_id: str):
    """Fetch the logged-in user's profile details."""
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id, user_name, user_address, email, latitude, longitude FROM users WHERE user_id = %s",
                    (user_id,),
                )
                return cur.fetchone()
    except Exception as e:
        print("DB get_user_profile error:", e)
        return None

def update_user_location(user_id: str, latitude: str, longitude: str):
    """Update a user's saved location coordinates."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET latitude = %s, longitude = %s WHERE user_id = %s",
                    (latitude, longitude, user_id),
                )
                conn.commit()
                return True
    except Exception as e:
        print("DB update_user_location error:", e)
        return False
