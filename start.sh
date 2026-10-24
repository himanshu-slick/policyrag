#!/bin/sh
# Start a bundled Postgres unless DATABASE_URL points at an external one, then ingest and serve.
set -e
if [ -z "$DATABASE_URL" ]; then
  PGDATA=/home/user/pgdata
  [ -d "$PGDATA" ] || initdb -D "$PGDATA" -U policyrag --auth=trust >/dev/null
  pg_ctl -D "$PGDATA" -o "-k /tmp -p 5432" -l /tmp/pg.log -w start >/dev/null
  createdb -h /tmp -U policyrag policyrag 2>/dev/null || true
  export DATABASE_URL="postgresql://policyrag@localhost:5432/policyrag"
fi
python -m policyrag.ingest
exec uvicorn policyrag.api:app --host 0.0.0.0 --port "${PORT:-7860}"
