"""Small SQLite persistence layer for leaderboard submissions."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    telegram_handle TEXT NOT NULL,
    duration_ms INTEGER NOT NULL CHECK (duration_ms > 0),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS submissions_ranking_idx
    ON submissions (duration_ms ASC, created_at ASC, id ASC);
"""


def _connect(database_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    return connection


def initialize(database_path: str | Path) -> None:
    """Create the database directory and schema if they do not exist."""

    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with _connect(path) as connection:
        connection.executescript(SCHEMA)


def add_submission(
    database_path: str | Path,
    *,
    name: str,
    phone_number: str,
    telegram_handle: str,
    duration_ms: int,
) -> dict[str, str | int]:
    """Store a submission and return only the fields safe for public use."""

    created_at = datetime.now(UTC).isoformat()
    with _connect(database_path) as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM submissions
            WHERE name = ? AND telegram_handle = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (name, telegram_handle),
        ).fetchone()

        if existing is None:
            connection.execute(
                """
                INSERT INTO submissions
                    (name, phone_number, telegram_handle, duration_ms, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, phone_number, telegram_handle, duration_ms, created_at),
            )
        else:
            connection.execute(
                """
                UPDATE submissions
                SET phone_number = ?, duration_ms = ?, created_at = ?
                WHERE id = ?
                """,
                (phone_number, duration_ms, created_at, existing["id"]),
            )

    return {
        "name": name,
        "duration_ms": duration_ms,
        "created_at": created_at,
    }


def leaderboard(database_path: str | Path) -> list[dict[str, str | int]]:
    """Read leaderboard rows without selecting locally stored contact details."""

    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT name, duration_ms, created_at
            FROM submissions
            ORDER BY duration_ms ASC, created_at ASC, id ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def admin_submissions(database_path: str | Path) -> list[dict[str, str | int]]:
    """Read every submission, including contact details, fastest first."""

    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, name, phone_number, telegram_handle, duration_ms, created_at
            FROM submissions
            ORDER BY duration_ms ASC, created_at ASC, id ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def delete_submission(database_path: str | Path, submission_id: int) -> bool:
    """Delete one submission and report whether it existed."""

    with _connect(database_path) as connection:
        cursor = connection.execute(
            "DELETE FROM submissions WHERE id = ?",
            (submission_id,),
        )

    return cursor.rowcount == 1
