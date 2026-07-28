import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helpers.db import get_conn  # noqa: E402

DEFAULT_SCHEMA = os.getenv("PGSCHEMA", "flowtrack_raw")


@pytest.fixture(scope="session")
def conn():
    """
    Session-scoped PostgreSQL connection fixture (env/.env via helpers.db).
    Sets search_path so tests can use bare table names.
    """
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DEFAULT_SCHEMA}, public;")
    yield conn
    conn.close()
