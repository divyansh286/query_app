from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
import sqlite3
import os
from datetime import datetime
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data.db"

app = Flask(__name__)
MAX_DB_MB = 500
TARGET_DB_MB = 450

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT NOT NULL,
                transformed_text TEXT NOT NULL,
                transform_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

def enforce_db_size():
    if not DB_PATH.exists():
        return
    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    if size_mb <= MAX_DB_MB:
        return
    with get_conn() as conn:
        # Delete oldest rows until the file can be compacted under target size.
        while size_mb > TARGET_DB_MB:
            row = conn.execute(
                "SELECT id FROM entries ORDER BY id ASC LIMIT 1"
            ).fetchone()
            if not row:
                break
            conn.execute("DELETE FROM entries WHERE id = ?", (row["id"],))
            conn.commit()
            conn.execute("VACUUM")
            size_mb = DB_PATH.stat().st_size / (1024 * 1024)


def transform_text(text: str, ttype: str) -> str:
    if ttype == "upper":
        return text.upper()
    if ttype == "lower":
        return text.lower()
    if ttype == "reverse":
        return text[::-1]
    if ttype == "trim":
        return " ".join(text.split())
    return text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        raw_text = request.form.get("query", "").strip()
        ttype = request.form.get("transform", "upper")
        if raw_text:
            transformed = transform_text(raw_text, ttype)
            with get_conn() as conn:
                conn.execute(
                    "INSERT INTO entries (raw_text, transformed_text, transform_type, created_at) VALUES (?, ?, ?, ?)",
                    (raw_text, transformed, ttype, datetime.utcnow().isoformat(timespec="seconds"))
                )
            enforce_db_size()
            return redirect(url_for("index"))

    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM entries ORDER BY id DESC LIMIT 50").fetchall()

    return render_template("index.html", rows=rows)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
