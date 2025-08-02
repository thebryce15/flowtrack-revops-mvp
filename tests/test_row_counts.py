import pytest

# Expected (min_rows, max_rows) for a quick‑sanity row‑count check.
# Upper bounds are deliberately generous so the test passes even as the
# dataset grows, while the non‑zero lower bounds flag empty tables.
TABLE_BANDS = {
    "marketing_spend":      (1, 1_000_000),
    "campaigns":            (1, 100_000),
    "leads":                (1, 5_000_000),
    "accounts":             (1, 1_000_000),
    "contacts":             (1, 5_000_000),
    "opportunities":        (1, 1_000_000),
    "sales_activities":     (1, 10_000_000),
    "sales_reps":           (1, 1_000),
    "customers":            (1, 1_000_000),
    "subscriptions":        (1, 1_000_000),
    "product_usage":        (1, 50_000_000),
    "support_tickets":      (1, 1_000_000),
    "nps_scores":           (1, 1_000_000),
    "churn_events":         (0, 1_000_000),  # churn may be zero in early data
}

@pytest.mark.parametrize("table, band", TABLE_BANDS.items())
def test_row_count_band(conn, table, band):
    """Ensure each table's row count is within the expected (min, max) band."""
    min_rows, max_rows = band
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        (count,) = cur.fetchone()
    assert min_rows <= count <= max_rows, (
        f"{table} has {count} rows, expected between {min_rows} and {max_rows}"
    )
