import pytest

# (child_table, child_column, parent_table, parent_column)
FK_PAIRS = [
    ("marketing_spend",  "campaign_id",  "campaigns",      "campaign_id"),
    ("leads",            "campaign_id",  "campaigns",      "campaign_id"),
    ("leads",            "account_id",   "accounts",       "account_id"),
    ("contacts",         "account_id",   "accounts",       "account_id"),
    ("opportunities",    "account_id",   "accounts",       "account_id"),
    ("opportunities",    "contact_id",   "contacts",       "contact_id"),
    ("opportunities",    "sales_rep_id", "sales_reps",     "rep_id"),
    ("sales_activities", "opportunity_id","opportunities", "opportunity_id"),
    ("sales_activities", "account_id",   "accounts",       "account_id"),
    ("sales_activities", "rep_id",       "sales_reps",     "rep_id"),
    ("customers",        "account_id",   "accounts",       "account_id"),
    ("subscriptions",    "customer_id",  "customers",      "customer_id"),
    ("product_usage",    "customer_id",  "customers",      "customer_id"),
    ("support_tickets",  "customer_id",  "customers",      "customer_id"),
    ("nps_scores",       "customer_id",  "customers",      "customer_id"),
    ("churn_events",     "customer_id",  "customers",      "customer_id"),
]

@pytest.mark.parametrize(
    "child, child_col, parent, parent_col", FK_PAIRS, ids=[
        f"{c}.{cc}->{p}.{pc}" for c, cc, p, pc in FK_PAIRS
    ]
)
def test_fk_integrity(conn, child, child_col, parent, parent_col):
    """
    Assert there are zero orphan rows for every declared FK pair.
    """
    sql = f"""
        SELECT COUNT(*) 
        FROM {child} c
        LEFT JOIN {parent} p
          ON c.{child_col} = p.{parent_col}
        WHERE c.{child_col} IS NOT NULL
          AND p.{parent_col} IS NULL;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        (orphans,) = cur.fetchone()
    assert orphans == 0, f"{child}.{child_col} has {orphans} orphan references to {parent}.{parent_col}"
