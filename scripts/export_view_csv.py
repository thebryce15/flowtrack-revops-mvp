# from repo root

import os, pandas as pd, psycopg2, pathlib, textwrap, sys
OUT = pathlib.Path("data/processed"); OUT.mkdir(parents=True, exist_ok=True)
conn = psycopg2.connect(
    host=os.getenv("PGHOST","localhost"), port=5432,
    dbname="flowtrack_data", user="postgres", password="admin")
views = {
    "vw_marketing_funnel":  "marketing_funnel.csv",
    "vw_sales_pipeline":    "sales_pipeline.csv",
    "vw_cs_health":         "cs_health.csv",
    "vw_finance_overview":  "finance_overview.csv",
}
for view, fn in views.items():
    print(f"Exporting {view} → {fn}")
    df = pd.read_sql(f"SELECT * FROM flowtrack_analytics.{view}", conn)
    df.to_csv(OUT / fn, index=False)
print("All view extracts saved to", OUT)
