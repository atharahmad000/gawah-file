"""Connections to operational data. Graph checkpoints have their own database."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def data_path(variable="GAWAH_OPS_DB", default="data/gawah_ops.db"):
    path = Path(os.getenv(variable, default))
    return path if path.is_absolute() else ROOT / path


def as_of(value=None):
    return datetime.fromisoformat(value or os.getenv("GAWAH_AS_OF", "2026-09-01T12:00:00")).strftime("%Y-%m-%d %H:%M:%S")


def get_conn():
    path = data_path()
    graph_path = data_path("GAWAH_GRAPH_DB", "data/gawah_graph.db")
    if path.resolve() == graph_path.resolve():
        raise ValueError("Operational and checkpoint databases must be separate")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


@contextmanager
def connect():
    conn = get_conn()
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def rows(sql, params=()):
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params)]


def one(sql, params=()):
    result = rows(sql, params)
    return result[0] if result else None
