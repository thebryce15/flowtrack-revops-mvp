/* ---------------------------------------------------------------------------
   View  : flowtrack_analytics.vw_finance_overview
   Purpose: Fiscal‑year ARR lens with new, expansion, churn and net retention.

   Definitions
   -----------
     • Fiscal year = calendar year (2023, 2024 in this data set).
     • Starting‑ARR  : ARR in force at 00:00 on 1‑Jan‑YYYY.
     • New‑ARR       : first‑ever subscription for a customer that starts in FY.
     • Expansion‑ARR : additional subscriptions (same customer) that start in FY.
     • Churn‑ARR     : ARR in force at the churn date, valued at monthly_value * 12.
     • ARR‑End       : ARR in force at 23:59 on 31‑Dec‑YYYY.
     • Net Retention % = (Starting‑ARR + Expansion‑ARR – Churn‑ARR) / Starting‑ARR * 100
                         (New‑ARR excluded by convention).

   Notes
   -----
     • ARR value = monthly_value * 12.
     • A customer can hold multiple parallel subscriptions (treated independently).
   --------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW flowtrack_analytics.vw_finance_overview AS
WITH year_dim AS (
    SELECT yr::int                    AS fiscal_year,
           make_date(yr, 1, 1)        AS year_start,
           make_date(yr, 12, 31)      AS year_end
    FROM generate_series(2023, 2024)  AS g(yr)
),

subs AS (
    SELECT
        s.subscription_id,
        s.customer_id,
        s.start_date,
        COALESCE(s.end_date, DATE '2999-12-31') AS end_date,
        s.monthly_value * 12                    AS arr
    FROM flowtrack_raw.subscriptions s
),

starting_arr AS (
    SELECT
        y.fiscal_year,
        SUM(s.arr) AS starting_arr
    FROM year_dim y
    JOIN subs s
      ON s.start_date <  y.year_start
     AND s.end_date   >= y.year_start
    GROUP BY 1
),

arr_end AS (
    SELECT
        y.fiscal_year,
        SUM(s.arr) AS arr_end
    FROM year_dim y
    JOIN subs s
      ON s.start_date <= y.year_end
     AND s.end_date   >  y.year_end
    GROUP BY 1
),

first_sub_per_cust AS (
    SELECT DISTINCT ON (customer_id)
        customer_id,
        start_date
    FROM subs
    ORDER BY customer_id, start_date
),

new_and_expansion AS (
    SELECT
        y.fiscal_year,
        SUM(CASE
              WHEN fs.customer_id IS NOT NULL THEN s.arr    -- first ever = NEW
              ELSE 0
            END)                            AS new_arr,
        SUM(CASE
              WHEN fs.customer_id IS NULL THEN s.arr        -- additional = EXPANSION
              ELSE 0
            END)                            AS expansion_arr
    FROM year_dim y
    JOIN subs s
      ON s.start_date BETWEEN y.year_start AND y.year_end
    LEFT JOIN first_sub_per_cust fs
           ON fs.customer_id = s.customer_id
          AND fs.start_date  = s.start_date                -- matches if first ever
    GROUP BY 1
),

churn_arr AS (
    SELECT
        y.fiscal_year,
        SUM(s.arr) AS churn_arr
    FROM year_dim y
    JOIN flowtrack_raw.churn_events ce
      ON ce.churn_date BETWEEN y.year_start AND y.year_end
    JOIN subs s
      ON s.customer_id = ce.customer_id
     AND s.start_date <= ce.churn_date
     AND s.end_date   >= ce.churn_date   -- in force at churn; prevents fan-out
                                         -- across a customer's earlier subs
    GROUP BY 1
)

SELECT
    y.fiscal_year,
    COALESCE(sa.starting_arr, 0)                  AS starting_arr,
    COALESCE(ne.new_arr, 0)                       AS new_arr,
    COALESCE(ne.expansion_arr, 0)                 AS expansion_arr,
    COALESCE(ca.churn_arr, 0)                     AS churn_arr,
    COALESCE(ae.arr_end, 0)                       AS arr_end,
    ROUND(
        CASE
            WHEN COALESCE(sa.starting_arr, 0) = 0 THEN NULL
            ELSE
              (COALESCE(sa.starting_arr, 0)
               + COALESCE(ne.expansion_arr, 0)
               - COALESCE(ca.churn_arr, 0))
               / sa.starting_arr::numeric * 100
        END
    , 2)                                          AS net_retention_pct
FROM year_dim              y
LEFT JOIN starting_arr      sa USING (fiscal_year)
LEFT JOIN arr_end           ae USING (fiscal_year)
LEFT JOIN new_and_expansion ne USING (fiscal_year)
LEFT JOIN churn_arr         ca USING (fiscal_year)
ORDER BY y.fiscal_year;
