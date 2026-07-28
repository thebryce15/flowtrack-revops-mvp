#!/usr/bin/env python
"""
FlowTrack — export the four analytic views to data/processed/ as the
dashboard-feeding CSVs. Run from the repo root after the views exist.
"""

import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from helpers.db import get_conn  # noqa: E402

OUT = pathlib.Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

VIEWS = {
    "vw_marketing_funnel": "marketing_funnel.csv",
    "vw_sales_pipeline": "sales_pipeline.csv",
    "vw_cs_health": "cs_health.csv",
    "vw_finance_overview": "finance_overview.csv",
}


def main() -> None:
    conn = get_conn()
    for view, fn in VIEWS.items():
        print(f"Exporting {view} -> {fn}")
        df = pd.read_sql(f"SELECT * FROM flowtrack_analytics.{view}", conn)
        df.to_csv(OUT / fn, index=False)
    conn.close()
    print("All view extracts saved to", OUT)


if __name__ == "__main__":
    main()
