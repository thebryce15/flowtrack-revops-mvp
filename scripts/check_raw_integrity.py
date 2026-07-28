#!/usr/bin/env python
"""
scripts/check_raw_integrity.py
--------------------------------
Sanity‑checks the FlowTrack *raw* layer:

1. Verifies that all 14 expected tables exist in schema `flowtrack_raw`.
2. Confirms each table’s row count falls within a reference band.
3. (Bonus) Flags orphaned rows for three critical FK relationships.

Exit code 0  → all checks pass  
Exit code 1  → at least one failure
"""

from pathlib import Path
import sys

# ensure project root is on import path 
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from tabulate import tabulate
from helpers.db import get_conn


# Configuration

EXPECTED_TABLES = [
    "marketing_spend",
    "leads",
    "accounts",
    "contacts",
    "opportunities",
    "sales_activities",
    "customers",
    "subscriptions",
    "product_usage",
    "support_tickets",
    "nps_scores",
    "churn_events",
    "campaigns",
    "sales_reps",
]

ROW_BANDS = {
    "marketing_spend": (1350, 1650),
    "leads": (63000, 77000),
    "accounts": (3600, 4400),
    "contacts": (7200, 8800),
    "opportunities": (5400, 6600),
    "sales_activities": (72000, 88000),
    "customers": (1800, 2200),
    "subscriptions": (2700, 3300),
    "product_usage": (187000, 229000),
    "support_tickets": (13500, 16500),
    "nps_scores": (2700, 3300),
    "churn_events": (315, 385),
    # campaigns & sales_reps => existence only
}

FK_CHECKS = [
    # child_table, child_column, parent_table, parent_column
    ("contacts", "account_id", "accounts", "account_id"),
    ("leads", "campaign_id", "campaigns", "campaign_id"),
    ("opportunities", "account_id", "accounts", "account_id"),
    ("subscriptions", "customer_id", "customers", "customer_id"),
]

SCHEMA = "flowtrack_raw"



# Helpers

def table_exists(cur, table_name: str) -> bool:
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM   information_schema.tables
            WHERE  table_schema = %s
              AND  table_name   = %s
        );
        """,
        (SCHEMA, table_name),
    )
    return cur.fetchone()[0]


def row_count(cur, table_name: str) -> int:
    cur.execute(f"SELECT COUNT(*) FROM {SCHEMA}.{table_name};")
    return cur.fetchone()[0]


def fk_orphans(cur, child_tbl, child_col, parent_tbl, parent_col) -> int:
    cur.execute(
        f"""
        SELECT COUNT(*)
        FROM   {SCHEMA}.{child_tbl}  AS c
        LEFT   JOIN {SCHEMA}.{parent_tbl} AS p
               ON  c.{child_col} = p.{parent_col}
        WHERE  c.{child_col} IS NOT NULL
          AND  p.{parent_col} IS NULL;
        """
    )
    return cur.fetchone()[0]



# Main routine

def main() -> None:
    conn = get_conn()
    cur = conn.cursor()

    # Table existence 
    presence_rows = []
    missing_tables = []
    for tbl in EXPECTED_TABLES:
        ok = table_exists(cur, tbl)
        presence_rows.append([tbl, "OK" if ok else "MISSING"])
        if not ok:
            missing_tables.append(tbl)

    # Row‑count bands 
    count_rows = []
    out_of_range = []
    for tbl, (lo, hi) in ROW_BANDS.items():
        if tbl in missing_tables:
            count_rows.append([tbl, "—", lo, hi, "TABLE MISSING"])
            out_of_range.append(tbl)
            continue
        cnt = row_count(cur, tbl)
        status = "OK" if lo <= cnt <= hi else "OUT OF RANGE"
        count_rows.append([tbl, cnt, lo, hi, status])
        if status != "OK":
            out_of_range.append(tbl)

    # FK integrity checks 
    fk_rows = []
    fk_issues = []
    for child_tbl, child_col, parent_tbl, parent_col in FK_CHECKS:
        if child_tbl in missing_tables or parent_tbl in missing_tables:
            fk_rows.append(
                [f"{child_tbl}.{child_col} → {parent_tbl}.{parent_col}", "—", "TABLE MISSING"]
            )
            fk_issues.append(child_tbl)
            continue
        orphans = fk_orphans(cur, child_tbl, child_col, parent_tbl, parent_col)
        status = "OK" if orphans == 0 else "ORPHANS"
        fk_rows.append(
            [f"{child_tbl}.{child_col} → {parent_tbl}.{parent_col}", orphans, status]
        )
        if status != "OK":
            fk_issues.append(child_tbl)

    cur.close()
    conn.close()

    # Print report 
    print("\n=== Table Presence ===")
    print(tabulate(presence_rows, headers=["Table", "Status"], tablefmt="github"))

    print("\n=== Row Counts ===")
    print(tabulate(count_rows, headers=["Table", "Actual", "Min", "Max", "Status"], tablefmt="github"))

    print("\n=== Foreign‑Key Integrity ===")
    print(tabulate(fk_rows, headers=["Relationship", "Orphans", "Status"], tablefmt="github"))

    # Exit code 
    has_errors = bool(missing_tables or out_of_range or fk_issues)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
