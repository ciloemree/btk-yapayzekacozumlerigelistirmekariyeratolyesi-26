"""Kampüs destek laboratuvarı: onay, talep ve denetim kayıtları (SQLite)."""
from __future__ import annotations
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(os.getenv("CAMPUS_DB", str(Path(__file__).resolve().parent / "kampus_talepler.sqlite3")))


def _connect():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=10000")
    return con


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as con:
        con.execute("CREATE TABLE IF NOT EXISTS approvals (token TEXT PRIMARY KEY, request_id TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0)")
        con.execute("CREATE TABLE IF NOT EXISTS tickets (request_id TEXT PRIMARY KEY, ad_soyad TEXT NOT NULL, esya TEXT NOT NULL, konum TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT, event TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL)")


def audit(request_id, event, details=""):
    init_db()
    with _connect() as con:
        con.execute("INSERT INTO audit(request_id,event,details,created_at) VALUES(?,?,?,?)",
                    (request_id, event, str(details)[:1000], datetime.now(timezone.utc).isoformat()))


def issue_approval(request_id):
    """Yalnızca insan onayı alındıktan sonra güvenilir uygulama kodu çağırır."""
    init_db()
    token = secrets.token_urlsafe(32)
    with _connect() as con:
        con.execute("INSERT INTO approvals(token,request_id) VALUES(?,?)", (token, request_id))
    audit(request_id, "human_approved")
    return token


def create_ticket(request_id, ad_soyad, esya, konum, approval_token):
    """Tek kullanımlık onay + request_id ile yinelenen kayıtları engeller."""
    init_db()
    if not all([request_id, ad_soyad.strip(), esya.strip(), konum.strip()]):
        return {"ok": False, "error": "Eksik başvuru alanı"}
    with _connect() as con:
        con.execute("BEGIN IMMEDIATE")
        old = con.execute("SELECT * FROM tickets WHERE request_id=?", (request_id,)).fetchone()
        if old:
            return {"ok": True, "duplicate": True, "ticket": dict(old)}
        approved = con.execute("SELECT used FROM approvals WHERE token=? AND request_id=?", (approval_token, request_id)).fetchone()
        if not approved or approved["used"]:
            return {"ok": False, "error": "Geçerli insan onayı bulunamadı"}
        now = datetime.now(timezone.utc).isoformat()
        con.execute("INSERT INTO tickets VALUES(?,?,?,?,?,?)",
                    (request_id, ad_soyad.strip(), esya.strip(), konum.strip(), "acik", now))
        con.execute("UPDATE approvals SET used=1 WHERE token=?", (approval_token,))
    audit(request_id, "ticket_created", json.dumps({"esya": esya, "konum": konum}, ensure_ascii=False))
    return {"ok": True, "duplicate": False, "ticket": get_ticket(request_id)}


def get_ticket(request_id):
    init_db()
    with _connect() as con:
        row = con.execute("SELECT * FROM tickets WHERE request_id=?", (request_id,)).fetchone()
        return dict(row) if row else None


def recent_audit(limit=30):
    init_db()
    with _connect() as con:
        return [dict(row) for row in con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (max(1, min(limit, 100)),))]
