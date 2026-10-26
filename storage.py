import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).with_name("reviews.db")

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            job_title TEXT NOT NULL,
            score INTEGER NOT NULL,
            status TEXT NOT NULL,
            reviewer TEXT,
            notes TEXT,
            criteria_json TEXT,
            created_at TEXT NOT NULL
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            detail TEXT,
            created_at TEXT NOT NULL
        )
        """)

def save_review(filename, job_title, score, status, reviewer, notes, criteria_json):
    with _connect() as conn:
        conn.execute(
            "INSERT INTO reviews(filename, job_title, score, status, reviewer, notes, criteria_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (filename, job_title, int(score), status, reviewer, notes, criteria_json, datetime.now().isoformat(timespec="seconds"))
        )

def list_reviews():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM reviews ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

def delete_review(record_id):
    with _connect() as conn:
        conn.execute("DELETE FROM reviews WHERE id = ?", (int(record_id),))

def log_event(event, detail=""):
    with _connect() as conn:
        conn.execute("INSERT INTO audit_events(event, detail, created_at) VALUES (?, ?, ?)",
                     (event, detail[:500], datetime.now().isoformat(timespec="seconds")))
