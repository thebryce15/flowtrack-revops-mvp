-- South‑region churn events in Q3 2024 (schema‑qualified)
SELECT
    ce.customer_id,
    ce.churn_date,
    ce.reason,
    ce.region
FROM flowtrack_raw.churn_events AS ce
WHERE ce.region = 'South'
  AND ce.churn_date >= '2024-07-01'
  AND ce.churn_date <  '2024-10-01';