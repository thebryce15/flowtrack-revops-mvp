# Year-in-Review rebuild — build spec (2026-07-28)

Replaces `YearInReview_2024.pbix/.pdf`. Every number below is verified against
the rebuilt Postgres pipeline (commit `38b3aa1`); the deck must tie to these
exactly. Old deck defects this rebuild retires: pipeline bookings showed $0
(status-case bug), the funnel page labeled all-time totals as FY24, the stage
legend contradicted the data, NDR was computed on a churn fan-out.

## Setup

1. Theme: `dashboards/theme/bryceos-precision-instrument.json`
   (View → Browse for themes). Install the Inter and Sora font families first
   or Power BI silently falls back to Segoe.
2. Data (Get Data → Text/CSV, import mode — deck stays self-contained):
   - `data/processed/finance_overview.csv`
   - `data/processed/fy_kpis_combined.csv`
   - `data/processed/marketing_funnel.csv`
   - `data/processed/sales_pipeline.csv`
   - `data/processed/cs_health.csv`
   - `raw_csv/subscriptions.csv` (waterfall basis)
   - `raw_csv/churn_events.csv` (spotlight page)
3. Design rules (match the site): dark canvas, one blue accent for data,
   neutral gray for context series, no shadows, no visual headers, direct
   labels over legends where possible, every big number carries a one-line
   qualifier textbox under it.

## Pages (6 total — cut the restated-pivot page and Look-Ahead)

### 0 · Title
"FlowTrack — FY2023–24 Year in Review". Subtitle: "Synthetic B2B SaaS ·
built end-to-end: PostgreSQL → QA → KPI extracts → this deck". Author line.

### 1 · Executive summary
Cards (value · qualifier):
- Ending ARR **$69.3M** · "+79% vs FY23 ($38.7M)"
- New ARR **$40.6M** · "first-ever subscriptions started in FY24"
- NDR **81.5%** · "(start + expansion − churn) / start; churn = ARR in force at churn date"
- Pipeline bookings **$54.4M** · "won opportunities closed in FY24"
Hero visual — ARR waterfall FY24 (single basis, foots exactly):
Start **38.74** → +Started **40.64** → −Ended **10.08** → End **69.30** ($M).
Qualifier: "subscription starts/ends during FY24; the churn-event lens
(NDR card) is a separate basis and intentionally not mixed in".
DAX (subscriptions): `Started FY24 = CALCULATE(SUMX(subscriptions,
subscriptions[monthly_value]*12), YEAR(subscriptions[start_date])=2024)`;
Ended likewise on `end_date` (blank end_date = still active, excluded).

### 2 · Marketing funnel
Line chart, monthly Jan-23→Dec-24: leads / MQLs / SQLs (from
marketing_funnel: count by month of lead_created; sum of mql_flag, sql_flag).
Leads in accent, MQL/SQL in supporting blues. Cards: SQLs **5,780** ·
"+33% vs FY23 (4,349)"; Lead→MQL **20.1%**, MQL→SQL **71.9%** (FY24).
Callout label on peak: **4,766 leads, Feb-24** (the old deck's "170% / Jan-24"
claim is retired — annual lead growth is +34%).

### 3 · Sales pipeline
Funnel on `current_stage` for OPEN opportunities created FY24
(Qualification → Negotiation; readable names, not the numeric stage codes the
old legend got wrong). Beside it, closed-FY24 outcome bar: won 1,121 · lost
305. Cards: Bookings **$54.4M** · Avg deal **$48.6K** (won, closed FY24) ·
Win rate **78.6%** · "of opportunities closed in FY24".

### 4 · Customer health
- Weekly support-ticket line (cs_health.ticket_volume by week_start — the
  week alignment is fixed; all 15,000 tickets are in the panel).
- Monthly avg NPS line. Card: NPS **7.1** · "FY24 average, 1–10 scale".
- Card: customer churn **17.5%** · "350 of 2,000 customers, all-time".

### 5 · Churn spotlight — South, Q3-24
The deliberately generated anomaly. Bar: churned customers by region for
Q3-24 (South = 39 of 81 = 48% of the quarter). Top-3 reasons: competitor 11 ·
support 8 · product_fit 8. Card: ARR lost **$1,617,202** · "subscriptions in
force at the churn date" (old $2.27M figure was a join fan-out; retired).
DAX: `ARR Lost = SUMX(FILTER(subscriptions, subscriptions[customer_id] IN
churned && subscriptions[start_date] <= churn_date && (ISBLANK(end_date) ||
end_date >= churn_date)), monthly_value*12)` — or import the number from the
regenerated deep-dive if simpler.

## Capture list (after build)

1. Export deck PDF → `dashboards/YearInReview_2024.pdf` (overwrite).
2. Save pbix → `dashboards/YearInReview_2024.pbix`.
3. PNG captures at 1920w: Exec summary, Funnel, Churn spotlight →
   `docs/assets/` (montage source + site figure wells).
4. Update README: "7 Power BI slides" → "6", restore the montage img block.
