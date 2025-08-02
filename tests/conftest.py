import os
import psycopg2
import pytest

DEFAULT_SCHEMA = os.getenv("PGSCHEMA", "flowtrack_raw") 

@pytest.fixture(scope="session")
def conn():
    """
    Session‑scoped PostgreSQL connection fixture.

    • Enables autocommit *before* any session commands to avoid the
      “set_session cannot be used inside a transaction” error.
    • Sets search_path so tests can use bare table names.
    """
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", 5432)),
        dbname=os.getenv("PGDATABASE", "flowtrack_data"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "admin"),
    )
    conn.autocommit = True                  
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {DEFAULT_SCHEMA}, public;")
    yield conn
    conn.close()
