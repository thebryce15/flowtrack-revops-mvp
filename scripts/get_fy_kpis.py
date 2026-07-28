#!/usr/bin/env python
"""
FlowTrack – Fiscal‑Year KPI extractor (Task 5)

• Hard‑codes FY 2023 & 2024.
• Queries analytic views, writes one CSV per FY under data/processed/,
  and prints a markdown‑style summary table for quick eyeballing.
"""

import pathlib
import sys
from textwrap import dedent

import pandas as pd
from tabulate import tabulate

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from helpers.db import get_conn  # noqa: E402


SQL_TEMPLATE = dedent(
    """
    WITH marketing AS (
        SELECT
            COUNT(DISTINCT lead_id)                        AS new_leads,
            SUM(CASE WHEN mql_flag THEN 1 END)             AS mqls,
            SUM(CASE WHEN sql_flag THEN 1 END)             AS sqls
        FROM flowtrack_analytics.vw_marketing_funnel
        WHERE lead_created >= DATE '{year}-01-01'
          AND lead_created  < DATE '{next_year}-01-01'

    ), sales AS (
        SELECT
            COALESCE(SUM(amount_usd), 0)                   AS pipeline_bookings,
            AVG(amount_usd)                                AS avg_deal_size
        FROM flowtrack_analytics.vw_sales_pipeline
        WHERE status = 'won'
          AND actual_close >= DATE '{year}-01-01'
          AND actual_close  < DATE '{next_year}-01-01'

    ), finance AS (
        SELECT
            starting_arr      AS arr_start,
            arr_end,
            net_retention_pct AS net_dollar_retention_pct
        FROM flowtrack_analytics.vw_finance_overview
        WHERE fiscal_year = {year}
    )

    SELECT
        {year}                                            AS fiscal_year,
        m.new_leads,
        m.mqls,
        m.sqls,
        ROUND(m.mqls::numeric / NULLIF(m.new_leads,0),4)  AS lead_to_mql_pct,
        ROUND(m.sqls::numeric / NULLIF(m.mqls,0),4)       AS mql_to_sql_pct,
        s.pipeline_bookings,
        s.avg_deal_size,
        f.arr_start,
        f.arr_end,
        f.net_dollar_retention_pct
    FROM marketing m
    CROSS JOIN sales    s
    CROSS JOIN finance  f;
    """
)

OUT_DIR = pathlib.Path("data/processed")


def kpis_for_year(conn, year: int) -> pd.DataFrame:
    """Return one‑row KPI DataFrame for the given fiscal year."""
    sql = SQL_TEMPLATE.format(year=year, next_year=year + 1)
    return pd.read_sql(sql, conn)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with get_conn() as conn:
        df_2023 = kpis_for_year(conn, 2023)
        df_2024 = kpis_for_year(conn, 2024)

    # Save tidy CSVs (per-FY + combined)
    df_2023.to_csv(OUT_DIR / "fy2023_kpis.csv", index=False)
    df_2024.to_csv(OUT_DIR / "fy2024_kpis.csv", index=False)
    df_all = pd.concat([df_2023, df_2024], ignore_index=True)
    df_all.to_csv(OUT_DIR / "fy_kpis_combined.csv", index=False)

    print("\nWrote fy2023_kpis.csv, fy2024_kpis.csv, fy_kpis_combined.csv to", OUT_DIR)
    print("\nFiscal‑Year KPI Summary")
    print(tabulate(df_all, headers="keys", showindex=False, tablefmt="github"))


if __name__ == "__main__":
    main()
