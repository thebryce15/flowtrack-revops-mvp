/* -------------------------------------------------------------------------
   View  : flowtrack_analytics.vw_cs_health
   Weekly customer health panel.

   Time key
   --------
   week_idx = 1..104 sequential index
              1  = ISO week 1 of 2023 (Mon 02-Jan-2023)
              53 = ISO week 1 of 2024 (Mon 01-Jan-2024)

   MetrIcs
   -------
     active_users_pct = active_users / logins * 100
     ticket_volume    = tickets opened that week
     latest_nps_score = most recent NPS that week
--------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW flowtrack_analytics.vw_cs_health AS
WITH usage_anchor AS (
    SELECT
        pu.customer_id,
        pu.week                                     AS week_idx,
        (DATE '2023-01-02' + (pu.week - 1) * INTERVAL '7 days')::date
                                                   AS week_start,
        pu.active_users,
        pu.logins,
        pu.workflows_run
    FROM flowtrack_raw.product_usage pu
),
tickets_week AS (
    SELECT
        st.customer_id,
        ((EXTRACT(year FROM st.created_at)::int - 2023) * 52
         + EXTRACT(week FROM st.created_at)::int)     AS week_idx,
        COUNT(*)                                      AS ticket_volume
    FROM flowtrack_raw.support_tickets st
    GROUP BY 1, 2
),
nps_week AS (
    SELECT DISTINCT ON (customer_id, week_idx)
        customer_id,
        week_idx,
        score                                        AS latest_nps_score
    FROM (
        SELECT
            customer_id,
            ((EXTRACT(year FROM date)::int - 2023) * 52
             + EXTRACT(week FROM date)::int)         AS week_idx,
            date,
            score
        FROM flowtrack_raw.nps_scores
    ) sub
    ORDER BY customer_id, week_idx, date DESC
),
subs_latest AS (
    SELECT DISTINCT ON (customer_id)
        customer_id,
        plan,
        monthly_value
    FROM flowtrack_raw.subscriptions
    ORDER BY customer_id, start_date DESC
)
SELECT
    ua.customer_id,
    c.account_id,
    c.segment,
    c.status,
    ua.week_idx,
    ua.week_start,
    ua.active_users,
    ua.logins,
    ua.workflows_run,
    ROUND(
        CASE WHEN ua.logins > 0
             THEN ua.active_users::numeric / ua.logins * 100
        END, 2)                                      AS active_users_pct,
    COALESCE(tw.ticket_volume, 0)                    AS ticket_volume,
    nw.latest_nps_score,
    sl.plan,
    sl.monthly_value
FROM usage_anchor            ua
JOIN flowtrack_raw.customers  c  USING (customer_id)
LEFT JOIN tickets_week        tw ON tw.customer_id = ua.customer_id
                                 AND tw.week_idx   = ua.week_idx
LEFT JOIN nps_week            nw ON nw.customer_id = ua.customer_id
                                 AND nw.week_idx   = ua.week_idx
LEFT JOIN subs_latest         sl ON sl.customer_id = ua.customer_id;
