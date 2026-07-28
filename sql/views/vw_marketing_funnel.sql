/* ---------------------------------------------------------------------------
   View  : flowtrack_analytics.vw_marketing_funnel
   Purpose: Per‑lead panel to feed monthly funnel metrics.

   MQL  = lead with account_id (date = accounts.created_date)
   SQL  = account with at least one opportunity
          (date = earliest opportunities.created_at)

   Column list
     lead_id , lead_created , utm_source , utm_medium , utm_campaign ,
     campaign_id , month , mql_flag , sql_flag , mql_date , sql_date ,
     spend_usd
   --------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW flowtrack_analytics.vw_marketing_funnel AS
WITH spend_month AS (
    SELECT
        m.campaign_id,
        m.month::date         AS month,
        SUM(m.amount)         AS spend_usd
    FROM flowtrack_raw.marketing_spend m
    GROUP BY 1, 2
),
accounts_mql AS (
    SELECT
        a.account_id,
        a.created_date        AS mql_date
    FROM flowtrack_raw.accounts a
),
sql_dates AS (
    SELECT
        o.account_id,
        MIN(o.created_at)     AS sql_date
    FROM flowtrack_raw.opportunities o
    GROUP BY 1
)
SELECT
    l.lead_id,
    l.created_at                       AS lead_created,
    l.utm_source,
    l.utm_medium,
    l.utm_campaign,
    l.campaign_id,
    date_trunc('month', l.created_at)::date AS month,
    (l.account_id IS NOT NULL)         AS mql_flag,
    (sd.sql_date IS NOT NULL)          AS sql_flag,
    am.mql_date,
    sd.sql_date,
    sm.spend_usd
FROM flowtrack_raw.leads      l
LEFT JOIN accounts_mql        am ON l.account_id = am.account_id
LEFT JOIN sql_dates           sd ON l.account_id = sd.account_id
LEFT JOIN spend_month         sm
       ON  sm.campaign_id = l.campaign_id
       AND sm.month       = date_trunc('month', l.created_at)::date;
