"""
modules/database_handler.py
----------------------------
Centralised SQLite access layer.
All other modules import from here – keeps connection logic in one place.
"""

import sqlite3
import os
import bcrypt

# ── Resolve DB path relative to this file's location ──────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BASE, "database", "legal_sections.db")


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION HELPER
# ─────────────────────────────────────────────────────────────────────────────
def get_connection():
    """Return a sqlite3 connection with row_factory set for dict-like access."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}.\n"
            "Please run:  python database/create_database.py"
        )
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────────────────────────────────────
# LEGAL SECTIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_all_sections():
    """Return all legal sections as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM legal_sections ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_sections_by_keyword(keyword: str):
    """
    Full-text search: return rows whose keywords column contains the keyword.
    Case-insensitive.
    """
    conn   = get_connection()
    query  = "SELECT * FROM legal_sections WHERE LOWER(keywords) LIKE ?"
    rows   = conn.execute(query, (f"%{keyword.lower()}%",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_section_by_id(section_id: int):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM legal_sections WHERE id = ?", (section_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_section(section, crime_name, description, punishment, keywords):
    conn = get_connection()
    conn.execute(
        "INSERT INTO legal_sections (section, crime_name, description, punishment, keywords) "
        "VALUES (?, ?, ?, ?, ?)",
        (section, crime_name, description, punishment, keywords),
    )
    conn.commit()
    conn.close()


def update_section(section_id, section, crime_name, description, punishment, keywords):
    conn = get_connection()
    conn.execute(
        "UPDATE legal_sections SET section=?, crime_name=?, description=?, "
        "punishment=?, keywords=? WHERE id=?",
        (section, crime_name, description, punishment, keywords, section_id),
    )
    conn.commit()
    conn.close()


def delete_section(section_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM legal_sections WHERE id = ?", (section_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# USER AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────────────
def get_user(username: str):
    conn = get_connection()
    row  = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def create_user(username: str, plain_password: str, role: str = "user") -> bool:
    """Register a new user.  Returns True on success, False if username taken."""
    try:
        hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
        conn   = get_connection()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, role),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists


def get_all_users():
    conn  = get_connection()
    rows  = conn.execute("SELECT id, username, role, created_at FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(username: str):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────────────────────────────────────────
def save_report(username, input_text, summary, crime_types, ipc_sections, sentiment, bias_score):
    conn = get_connection()
    conn.execute(
        "INSERT INTO reports (username, input_text, summary, crime_types, "
        "ipc_sections, sentiment, bias_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, input_text, summary, crime_types, ipc_sections, sentiment, float(bias_score)),
    )
    conn.commit()
    conn.close()


def get_reports(username: str = None):
    conn = get_connection()
    if username:
        rows = conn.execute(
            "SELECT * FROM reports WHERE username = ? ORDER BY created_at DESC", (username,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
