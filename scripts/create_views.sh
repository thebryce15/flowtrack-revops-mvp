#!/usr/bin/env bash
# ------------------------------------------------------------------
# create_views.sh  – Idempotently (re)creates all analytic views
# ------------------------------------------------------------------
# Usage:
#   chmod +x scripts/create_views.sh
#   ./scripts/create_views.sh
#
# The script:
#   1. Reads .env (if present) for PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
#   2. Executes every *.sql file in sql/views/ via psql with ON_ERROR_STOP
#   3. Exits non‑zero if any view fails to compile
# ------------------------------------------------------------------

set -euo pipefail

# ----- Load env file so psql picks up connection vars -------------------------
if [[ -f ".env" ]]; then
  # shellcheck disable=SC2046,SC1091
  export $(grep -v '^#' .env | xargs)
fi

# ----- psql connection flags --------------------------------------------------
PGFLAGS="-v ON_ERROR_STOP=1 \
  --host=${PGHOST:-localhost} \
  --port=${PGPORT:-5432} \
  --username=${PGUSER:-postgres} \
  --dbname=${PGDATABASE:-flowtrack_data}"

echo "Creating analytic views in schema flowtrack_analytics ..."
for sql_file in sql/views/*.sql; do
  echo "  ➜  ${sql_file}"
  psql ${PGFLAGS} -f "${sql_file}"
done

echo "All analytic views created or replaced successfully."
