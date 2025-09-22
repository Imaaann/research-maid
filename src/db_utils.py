from pathlib import Path
import sqlite3
from typing import Optional

from .project import get_project_dir

_db_conn: Optional[sqlite3.Connection] = None
_db_path: Optional[Path] = None

_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS chunks (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        text     TEXT    NOT NULL,
        metadata TEXT    NOT NULL
    );
"""


def init_sqlite_db(project_name: str, db_filename: str = "chunks.db"):
    global _db_conn, _db_path
    projects_dir = get_project_dir(project_name)

    if _db_conn is not None:
        try:
            _db_conn.close()
        except Exception:
            pass
        _db_conn = None
        _db_path = None

    db_path = projects_dir / db_filename
    conn = sqlite3.connect(str(db_path), check_same_thread=False)

    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PARGMA journal_mode = WAL")
    except Exception:
        pass

    conn.execute(_CREATE_TABLE_SQL)
    conn.commit()

    _db_conn = conn
    _db_path = db_path
    return conn


def get_connection() -> sqlite3.Connection:
    if _db_conn is None:
        raise RuntimeError("Database not initialized run init_sqlite_db")
    return _db_conn


def close_connection():
    global _db_conn, _db_path
    if _db_conn is not None:
        try:
            _db_conn.close()
        finally:
            _db_conn = None
            _db_path = None
