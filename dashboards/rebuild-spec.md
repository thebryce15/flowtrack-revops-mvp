# FlowTrack Revenue Operations — instrument spec (2026-07-28, supersedes the deck rebuild)

Shape ratified: a 5-page **operating instrument** (the dashboard a revenue team
runs its weekly/monthly cadence on), not a year-in-review deck. The old
`YearInReview_2024.pbix/.pdf` retires when this ships. Every number below is
verified against the rebuilt pipeline (PG17, post-dedup); the build must tie
to these exactly.

**As-of convention:** the dataset ends 2024-12-31; the instrument freezes
"today" there. Small footer on every page: "Data as of Dec 31, 2024 ·
synthetic dataset". All aging / next-90-days math anchors to that date.

**Illustrative plan (ratified):** FY24 plan = $70.0M ARR exit, linear monthly
ramp from the FY23 exit ($38.74M); Q1-25 bookings target = $15.0M. Both are
DAX constants, always labeled "illustrative plan" on the visual. Actual
attainment lands at 99.0% — ahead early, narrow miss at close.

## Setup

1. Save as **.pbip** (Options → Preview features → Power BI Project files) —
   the model/measures become diffable TMDL source in the repo.
2. Theme `dashboards/theme/bryceos-precision-instrument.json`; install Inter +
   Sora fonts first or PBI silently falls back to Segoe.
3. Imports (Text/CSV, import mode): processed → `finance_overview`,
   `marketing_funnel`, `sales_pipeline`, `cs_health`; raw → `subscriptions`,
   `churn_events`, `campaigns`, `marketing_spend`, `opportunities`,
   `nps_scores`, `support_tickets`.
4. Design rules: dark canvas, one accent for data + neutral gray for context,
   no shadows, no visual headers, direct labels, every big number carries a
   one-line qualifier.

## Page 1 — Are we going to hit the number? (CEO/CRO · weekly)

- Hero: monthly ARR actual vs illustrative plan line, FY24
  (actuals, month-end, $M): 42.35 · 45.14 · 47.06 · 49.55 · 52.03 · 56.01 ·
  56.81 · 60.63 · 63.62 · 65.95 · 67.68 · **69.30**.
- Cards: Ending ARR **$69.3M** · "+79% vs FY23; 99.0% of illustrative plan" |
  NDR **81.5%** · "(start + expansion − churn) / start; churn = ARR in force
  at churn date" | Bookings FY24 **$54.4M** · "won, closed in FY24" |
  Qualified coverage **≈2.0×** · "open pipe ≤180 days old vs Q1-25 target —
  see page 3 for why raw coverage (7.5×) is a vanity number".
- ARR waterfall (single basis, foots exactly): 38.74 + 40.64 started − 10.08
  ended = 69.30. Qualifier: "subscription starts/ends; churn-event lens kept
  separate by design".

## Page 2 — Which marketing dollars buy revenue? (Marketing · monthly)

- Bar: **cost per SQL by source** (verified): referral **$1,135** · social
  **$1,188** · other_publicities $1,645 · email $1,728 · other $2,003 ·
  direct $2,297 · paid_search $2,321 · display **$2,705**. Callout: "a
  referral SQL costs 42% of a display SQL".
- Line: monthly leads / MQLs / SQLs, Jan-23→Dec-24; peak label 4,766 (Feb-24).
- Cards: SQLs FY24 **5,780** · "+33% vs FY23" | Lead→MQL **20.1%** ·
  MQL→SQL **71.9%** (FY24) | Total spend **$16.7M** · "FY23-24, all channels".
- Decision framing (textbox, one line): where the next dollar goes.

## Page 3 — Is the pipeline healthy, or just big? (Sales · weekly)

- THE story (verified): open pipe **$112.0M / 2,282 opps**, but **$82.7M
  (73.8%) is >180 days old** — ~3× the 62-day median close velocity. Aging
  bar: 0-90d $21.8M · 91-180d $7.6M · >180d $82.7M.
- Cards: Win rate FY24 **78.6%** · "of closed" | Median velocity **62 days** ·
  "created → closed-won" | Avg deal **$48.6K** | Touches per won deal
  **10.7** · "logged activities, FY24 wins".
- Funnel on `current_stage` (readable names) for open opps ≤180d.
- Decision: requalify or purge the stale 74%.

## Page 4 — Which customers are we about to lose? (CS · weekly)

- Anchor: **Q1-25 renewal exposure — $3.06M ARR / 85 subs / 73 customers**
  (active at as-of, end_date in Q1-25).
- Intervention list (table visual): the **15 flagged renewing customers**
  (latest NPS < 6: 10 · tickets ≥2 since Dec-1: 6, overlap 1) with segment,
  ARR, flag reason. This is the page's product: who gets a call this week.
- Trends: weekly ticket volume (alignment now correct; all 15,000 tickets in
  panel) · monthly avg NPS. Cards: NPS **7.1** · "FY24 avg, 1-10" | Customer
  churn **17.5%** · "350 of 2,000, all-time".
- Honesty note (spec-level, not on-canvas): usage_score has no pre-churn
  decline signal in this synthetic set — flags are level-based (NPS, tickets),
  not trend-based, and that is fine for the instrument's purpose.

## Page 5 — Why did we lose the ones we lost? (Exec · quarterly)

- Churn ARR by quarter (in-force-at-churn basis) + region×quarter matrix
  exposing the anomaly: **South Q3-24 = 39 of 81 churn events (48%)**.
- Top-3 reasons (South Q3-24): competitor 11 · support 8 · product_fit 8.
- Card: ARR lost, South Q3-24 **$1,617,202** · "subscriptions in force at the
  churn date".
- FY cards: churn ARR FY24 **$7.16M** · NDR **81.5%**.

## Capture list (after build)

1. Save `.pbip` under `dashboards/` (retire the old .pbix + PDF in the same
   commit); export a fresh PDF for the repo.
2. PNGs at 1920w → `docs/assets/`: pages 1, 3, 4 (site figure wells +
   montage source); rebuild montage.png; restore README img block; update
   README deliverables ("operating instrument, 5 pages" replaces "7 slides").
3. Test publish-to-web on the free account; if embed codes are allowed the
   site project page links/embeds the live instrument, else captures per the
   dashboard-demo ruling.
