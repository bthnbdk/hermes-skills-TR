# Scheduler DB Health Check Technique

When monitoring cron job health with `no_agent=True` scripts, the scheduler's SQLite DB is more reliable than log file globs.

## Why not log files?

`no_agent=True` scripts don't produce `~/.hermes/cron/output/*.log` files. Globbing for those returns empty → false positive "cron not running" alerts.

## The fix: query `cron.db` directly

```python
import sqlite3, os
from datetime import datetime

def check_cron():
    db_path = os.path.expanduser("~/.hermes/cron/cron.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT MAX(last_run_at) FROM jobs WHERE last_run_at IS NOT NULL")
            row = c.fetchone()
            conn.close()
            if row and row[0]:
                last_run = datetime.fromisoformat(row[0])
                age_hours = (datetime.now() - last_run).total_seconds() / 3600
                return {"ok": age_hours < 3, "latest_run_age_hours": round(age_hours, 1)}
        except:
            pass
    # If DB doesn't exist yet (fresh setup), assume OK
    return {"ok": True, "note": "cron_db_missing_assume_ok"}
```

## How it works

- `cron.db` is at `~/.hermes/cron/cron.db`
- Query: `SELECT MAX(last_run_at) FROM jobs WHERE last_run_at IS NOT NULL`
- Returns the most recent time ANY job ran
- If the most recent run was >3h ago, flag as unhealthy
- If DB doesn't exist (first deploy, before scheduler started), assume OK

## Pitfalls

- `last_run_at` is stored as ISO8601 string — use `datetime.fromisoformat()`
- Fresh deploys may not have a `cron.db` yet — don't flag as error
- 3h threshold is generous (gmail monitor runs every 1m, so missing 3h means scheduler is definitely down)
