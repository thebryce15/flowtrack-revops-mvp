/* ---------------------------------------------------------------------------
   View  : flowtrack_analytics.vw_sales_pipeline
   Purpose: Opportunity‑level snapshot that joins pipeline facts to
            account and sales‑rep context.  One row per opportunity.

   Columns
   -------
     opportunity_id      :: bigint
     created_at          :: timestamptz   – opportunity open date
     account_id          :: bigint
     account_name        :: text
     segment             :: text
     industry            :: text
     account_region      :: text
     amount_usd          :: numeric(12,2)
     pipeline_stage      :: smallint
     current_stage       :: text
     forecast_category   :: text
     next_step_date      :: date
     status              :: text
     actual_close        :: date
     loss_reason         :: text
     sales_rep_id        :: bigint
     rep_name            :: text
     rep_email           :: text
     rep_region          :: text
     rep_start_date      :: date
   --------------------------------------------------------------------------- */

CREATE OR REPLACE VIEW flowtrack_analytics.vw_sales_pipeline AS
SELECT
    o.opportunity_id,
    o.created_at,
    o.account_id,
    a.account_name,
    a.segment,
    a.industry,
    a.region           AS account_region,
    o.amount           AS amount_usd,
    o.pipeline_stage,
    o.current_stage,
    o.forecast_category,
    o.next_step_date,
    o.status,
    o.actual_close,
    o.loss_reason,
    o.sales_rep_id,
    r.name             AS rep_name,
    r.email            AS rep_email,
    r.region           AS rep_region,
    r.start_date       AS rep_start_date
FROM flowtrack_raw.opportunities o
JOIN flowtrack_raw.accounts     a  USING (account_id)
LEFT JOIN flowtrack_raw.sales_reps r
       ON  r.rep_id = o.sales_rep_id;
