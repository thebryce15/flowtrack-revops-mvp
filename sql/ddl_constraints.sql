/* ---------------------------------------------------------------------------
   FlowTrack — schema DDL + integrity constraints
   Creates flowtrack_raw (14 tables mirroring raw_csv/) and the empty
   flowtrack_analytics schema the views build into.

   Idempotent: drops and recreates both schemas. Run via scripts/load_raw.py,
   which executes this file and then COPYs the CSVs in FK-safe order.

   FK set mirrors tests/test_fk_integrity.py exactly — the constraints and the
   test suite assert the same 16 relationships.
   --------------------------------------------------------------------------- */

DROP SCHEMA IF EXISTS flowtrack_analytics CASCADE;
DROP SCHEMA IF EXISTS flowtrack_raw CASCADE;
CREATE SCHEMA flowtrack_raw;
CREATE SCHEMA flowtrack_analytics;

SET search_path TO flowtrack_raw, public;

CREATE TABLE campaigns (
    campaign_id  integer PRIMARY KEY,
    source       text,
    start_date   date,
    end_date     date,
    status       text,
    objective    text
);

CREATE TABLE accounts (
    account_id       integer PRIMARY KEY,
    account_name     text,
    domain           text,
    segment          text,
    industry         text,
    region           text,
    created_date     date,
    owner_id         integer,
    lifecycle_stage  text,
    last_activity_at timestamp,
    is_customer      boolean,
    is_churned       boolean
);

CREATE TABLE sales_reps (
    rep_id     integer PRIMARY KEY,
    name       text,
    email      text,
    region     text,
    start_date date,
    is_active  boolean
);

CREATE TABLE contacts (
    contact_id  integer PRIMARY KEY,
    account_id  integer REFERENCES accounts (account_id),
    first_name  text,
    last_name   text,
    email       text,
    title       text,
    phone       text,
    created_at  date,
    lead_source text,
    lead_status text
);

CREATE TABLE customers (
    customer_id  integer PRIMARY KEY,
    account_id   integer REFERENCES accounts (account_id),
    onboard_date date,
    segment      text,
    status       text
);

CREATE TABLE leads (
    lead_id      uuid PRIMARY KEY,
    created_at   date,
    utm_source   text,
    utm_medium   text,
    utm_campaign text,
    campaign_id  integer REFERENCES campaigns (campaign_id),
    account_id   integer REFERENCES accounts (account_id),
    first_name   text,
    last_name    text,
    email        text,
    phone        text
);

CREATE TABLE marketing_spend (
    campaign_id       integer REFERENCES campaigns (campaign_id),
    month             date,
    channel_cost_type text,
    amount            numeric(12,2),
    region            text
);

CREATE TABLE opportunities (
    opportunity_id    integer PRIMARY KEY,
    account_id        integer REFERENCES accounts (account_id),
    contact_id        integer REFERENCES contacts (contact_id),
    sales_rep_id      integer REFERENCES sales_reps (rep_id),
    created_at        date,
    amount            numeric(12,2),
    pipeline_stage    integer,
    current_stage     text,
    forecast_category text,
    next_step_date    date,
    status            text,
    actual_close      date,
    loss_reason       text
);

CREATE TABLE sales_activities (
    activity_id    integer PRIMARY KEY,
    opportunity_id integer REFERENCES opportunities (opportunity_id),
    account_id     integer REFERENCES accounts (account_id),
    rep_id         integer REFERENCES sales_reps (rep_id),
    type           text,
    timestamp      timestamp,
    outcome        text,
    notes          text,
    sequence_id    integer,
    sequence_step  integer
);

CREATE TABLE subscriptions (
    subscription_id integer PRIMARY KEY,
    customer_id     integer REFERENCES customers (customer_id),
    plan            text,
    start_date      date,
    end_date        date,
    monthly_value   numeric(10,2)
);

CREATE TABLE product_usage (
    customer_id      integer REFERENCES customers (customer_id),
    week             integer,
    usage_score      double precision,
    active_users     integer,
    logins           integer,
    workflows_run    integer,
    feature_x_events integer,
    feature_y_events integer,
    PRIMARY KEY (customer_id, week)
);

CREATE TABLE support_tickets (
    ticket_id           integer PRIMARY KEY,
    customer_id         integer REFERENCES customers (customer_id),
    created_at          date,
    resolved_at         date,
    category            text,
    status              text,
    cs_rep_id           integer,
    first_response_mins integer,
    resolution_mins     integer
);

CREATE TABLE nps_scores (
    nps_id         integer PRIMARY KEY,
    customer_id    integer REFERENCES customers (customer_id),
    date           date,
    score          numeric,
    notes          text,
    survey_channel text
);

CREATE TABLE churn_events (
    churn_event_id integer PRIMARY KEY,
    customer_id    integer REFERENCES customers (customer_id),
    churn_date     date,
    region         text,
    segment        text,
    reason         text
);
