#!/usr/bin/env python
"""
FlowTrack — one-shot database build.

Runs sql/ddl_constraints.sql (drops + recreates both schemas), then COPYs the
14 raw CSVs into flowtrack_raw in FK-safe order and prints per-table row
counts. After this, build the analytic views (scripts/create_views.sh or run
the files in sql/views/) and the rest of the pipeline works.

Usage (from repo root, .env configured):
    python scripts/load_raw.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helpers.db import get_conn  # noqa: E402

# FK-safe load order (parents before children).
TABLES = [
    "campaigns",
    "accounts",
    "sales_reps",
    "contacts",
    "customers",
    "leads",
    "marketing_spend",
    "opportunities",
    "sales_activities",
    "subscriptions",
    "product_usage",
    "support_tickets",
    "nps_scores",
    "churn_events",
]


def main() -> None:
    ddl = (ROOT / "sql" / "ddl_constraints.sql").read_text(encoding="utf-8")
    conn = get_conn()
    with conn.cursor() as cur:
        # campaigns.csv uses M/D/YYYY dates; everything else is ISO — MDY covers both.
        cur.execute("SET datestyle = 'ISO, MDY';")
        cur.execute(ddl)
        for table in TABLES:
            csv_path = ROOT / "raw_csv" / f"{table}.csv"
            with open(csv_path, encoding="utf-8") as f:
                cur.copy_expert(
                    f"COPY flowtrack_raw.{table} FROM STDIN "
                    "WITH (FORMAT csv, HEADER true, NULL '')",
                    f,
                )
            cur.execute(f"SELECT COUNT(*) FROM flowtrack_raw.{table}")
            print(f"  {table:<18} {cur.fetchone()[0]:>7,} rows")
    conn.close()
    print("Load complete. Next: bash scripts/create_views.sh")


if __name__ == "__main__":
    main()
