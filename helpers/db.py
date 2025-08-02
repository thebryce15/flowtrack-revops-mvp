"""
helpers/db.py
Utility for obtaining a PostgreSQL connection.
"""

from pathlib import Path
import os

from dotenv import load_dotenv
import psycopg2



# Internal helpers

_ENV_LOADED = False


def _load_env_file() -> None:
    """Load .env from project root once per process."""
    global _ENV_LOADED
    if _ENV_LOADED:  # already loaded
        return

    # Project root is two levels up from this file (helpers/db.py)
    root_dir = Path(__file__).resolve().parents[1]
    env_path = root_dir / ".env"

    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # Fall back to any .env discoverable via current working directory
        load_dotenv()

    _ENV_LOADED = True



# Public API

def get_conn():
    """
    Return a live psycopg2 connection using environment variables:
    PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE.
    Autocommit is enabled by default.

    Raises
    ------
    psycopg2.OperationalError
        If authentication fails or the server is unreachable.
    """
    _load_env_file()

    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", 5432),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "admin"),
        dbname=os.getenv("PGDATABASE", "flowtrack_data"),
    )
    conn.autocommit = True
    return conn


__all__ = ["get_conn"]
