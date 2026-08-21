"""Environment-backed application settings."""

import os

DEFAULT_DATABASE_PATH = "data/leaderboard.sqlite"
DEFAULT_ATTEMPT_TIME_LIMIT_SECONDS = 60


def database_path() -> str:
    """Return the configured SQLite path."""

    return os.environ.get("DATABASE_PATH") or DEFAULT_DATABASE_PATH


def submission_password() -> str:
    """Return the required password, failing when it is not configured."""

    password = os.environ.get("SUBMISSION_PASSWORD")
    if not password:
        raise RuntimeError("SUBMISSION_PASSWORD must be set")
    return password


def attempt_time_limit_seconds() -> int:
    """Return the configured attempt time limit, failing on invalid values."""

    value = os.environ.get("ATTEMPT_TIME_LIMIT_SECONDS")
    if value is None:
        return DEFAULT_ATTEMPT_TIME_LIMIT_SECONDS

    message = "ATTEMPT_TIME_LIMIT_SECONDS must be a strictly positive integer"
    try:
        limit = int(value)
    except ValueError as exc:
        raise RuntimeError(message) from exc

    if limit <= 0:
        raise RuntimeError(message)
    return limit


def attempt_time_limit_ms() -> int:
    """Return the configured attempt time limit in milliseconds."""

    return attempt_time_limit_seconds() * 1000
