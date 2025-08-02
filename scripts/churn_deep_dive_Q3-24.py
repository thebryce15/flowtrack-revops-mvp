"""
South‑Region Churn Deep‑Dive – Q3 2024
--------------------------------------

Creates:
    docs/reports/churn_reasons_q3_24.png
    docs/reports/churn_deep_dive_Q3-24.pdf

Usage (PowerShell, venv active):

    pip install fpdf2 pandas sqlalchemy matplotlib psycopg2-binary
    $env:FLOWTRACK_DB_URL = "postgresql+psycopg2://flow_admin:admin@localhost:5432/flowtrack_data"
    python scripts/churn_deep_dive_Q3-24.py
"""

import os
import pathlib

import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy as sa
from fpdf import FPDF


# 1.  Connect to PostgreSQL

DB_URL = os.getenv("FLOWTRACK_DB_URL")  # e.g. postgresql+psycopg2://user:pass@host/db
if not DB_URL:
    raise RuntimeError(
        "FLOWTRACK_DB_URL environment variable not set.\n"
        "Example:\n"
        "  $env:FLOWTRACK_DB_URL = "
        "\"postgresql+psycopg2://flow_admin:admin@localhost:5432/flowtrack_data\""
    )

engine = sa.create_engine(DB_URL)


# 2.  Pull South‑region churn events for Q3 2024

QUERY = """
SELECT
    ce.customer_id,
    ce.churn_date,
    ce.reason,
    COALESCE(s.monthly_value,0) * 12 AS arr_lost
FROM   flowtrack_raw.churn_events      AS ce
LEFT   JOIN flowtrack_raw.subscriptions AS s
           ON s.customer_id = ce.customer_id
WHERE  ce.region = 'South'
  AND  ce.churn_date >= DATE '2024-07-01'
  AND  ce.churn_date <  DATE '2024-10-01';
"""
df = pd.read_sql(QUERY, engine)

if df.empty:
    raise SystemExit("No churn rows returned for South region in Q3 2024.")


# 3.  Build bar chart of top 3 churn reasons

top = (
    df.groupby("reason")
      .agg(churn_count=("customer_id", "nunique"))
      .sort_values("churn_count", ascending=False)
      .head(3)
)

project_root = pathlib.Path(__file__).resolve().parent.parent
reports_dir  = project_root / "docs" / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

chart_path = reports_dir / "churn_reasons_q3_24.png"

fig, ax = plt.subplots()
top["churn_count"].plot(kind="bar", ax=ax)
ax.set_ylabel("Churned Customers")
ax.set_title("Top 3 Churn Reasons - South Q3 2024")

for bar, count in zip(ax.patches, top["churn_count"]):
    ax.annotate(str(count),
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center", va="bottom", fontsize=9)

fig.tight_layout()
fig.savefig(chart_path, dpi=300)
plt.close(fig)
print(f"Saved chart → {chart_path}")


# 4.  Build single‑page PDF with KPIs + chart

total_churn = df["customer_id"].nunique()
total_arr   = df["arr_lost"].sum()

pdf_path = reports_dir / "churn_deep_dive_Q3-24.pdf"
pdf = FPDF(orientation="L", unit="mm", format="A4")
pdf.set_auto_page_break(False)
pdf.add_page()

# Title
pdf.set_font("Helvetica", style="B", size=18)
pdf.cell(0, 12, "South-Region Churn Deep-Dive - Q3 2024", ln=True, align="C")

# KPI line
pdf.set_font("Helvetica", size=14)
pdf.cell(
    0,
    10,
    f"Churned Customers: {total_churn}    |    ARR Lost: ${total_arr:,.0f}",
    ln=True,
    align="C",
)

pdf.ln(4)  

# Insert full‑width chart (leave margins)
pdf.image(str(chart_path), x=20, y=40, w=250)

pdf.output(str(pdf_path))
print(f"Saved PDF → {pdf_path}")
