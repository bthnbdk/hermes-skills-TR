# ERPNext Setup Reference

## Docker Stack
- **Compose file:** `~/erpnext/docker-compose.yml`
- **Image:** `frappe/erpnext:v16.24.0`
- **URL:** http://localhost:8080
- **Admin:** Administrator / admin
- **Site:** frontend

## 10 Containers

| Container | Role | 
|-----------|------|
| backend | Gunicorn (Frappe app server, internal port 8000) |
| frontend | Nginx reverse proxy (external port 8080) |
| db | MariaDB 11.8 |
| redis-cache | Redis cache |
| redis-queue | Redis queue |
| queue-long | Long-running background worker |
| queue-short | Short-running background worker |
| scheduler | Frappe scheduler |
| websocket | Socket.IO server |
| configurator | (one-shot) common_site_config.json |
| create-site | (one-shot) bench new-site + install erpnext |

## Start / Stop

```bash
# Start Docker daemon (needed after WSL reboot)
sudo dockerd &
sudo chmod 666 /var/run/docker.sock

# Start ERPNext stack
docker compose -f ~/erpnext/docker-compose.yml up -d

# Stop
docker compose -f ~/erpnext/docker-compose.yml down

# Restart a single container
docker compose -f ~/erpnext/docker-compose.yml restart backend
```

## Status Checks

```bash
# Container health
docker compose -f ~/erpnext/docker-compose.yml ps

# HTTP health
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080

# Frappe ping
curl -s http://localhost:8080/api/method/frappe.ping
```

## Agent Cron Jobs

Managed by Hermes Agent scheduler. 13 active jobs:

| Script | Schedule | Agent |
|--------|----------|-------|
| `ithalat_gmail_monitor.py` | every 1m | Email Gateway |
| `ithalat_agent_orchestrator.py` | 1-59/2 | Orchestrator |
| `ithalat_agent_crm.py` | 2-59/3 | CRM |
| `ithalat_agent_supplier.py` | 3-59/3 | Supplier |
| `ithalat_agent_pricing.py` | 4-59/3 | Pricing |
| `ithalat_agent_research.py` | 6-59/5 | Research |
| `ithalat_agent_approval.py` | 5-59/5 | Approval Manager |
| `ithalat_agent_reporting.py` | 7-59/5 | Reporting |
| `ithalat_founder_notifier.py` | every 1h | (infra) |
| `ithalat_approval_orchestrator.py` | every 30m | (infra) |
| `ithalat_daily_report.py` | 09:00 daily | (infra) |
| `ithalat_health_checker.py` | every 5m | (infra) |
| `ithalat_trade_readiness.py` | 8-59/30 | Trade Readiness |

```bash
# List all cron jobs
hermes cron list
```

## Trigger Daemon (systemd user service)

Real-time Gmail polling: runs every 30s and triggers monitor + approval + notifier on new email.

```bash
# Status
systemctl --user status ithalat-trigger-daemon.service

# Logs (last 50 lines)
journalctl --user -u ithalat-trigger-daemon -n 50 --no-pager

# Restart
systemctl --user restart ithalat-trigger-daemon.service

# Stop
systemctl --user stop ithalat-trigger-daemon.service
```

## Script Directory

```bash
# All agent scripts
ls ~/.hermes/scripts/ithalat_*.py

# API helper (single session handling, CRUD, retry)
less ~/.hermes/scripts/ithalat_erpnext_api.py
```

## State Files

| File | Tracks |
|------|--------|
| `~/.hermes/ithalat_gmail_state.json` | Last email UID, sync timestamp |
| `~/.hermes/ithalat_health_alerts.json` | Last alert + last OK timestamp |
| `~/.hermes/ithalat_notifier_state.json` | Last notifier run |
