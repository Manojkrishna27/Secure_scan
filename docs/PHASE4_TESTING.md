# Phase 4 — Monitoring & Notifications Testing

## Prerequisites

```bash
cd backend && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
flask db upgrade
python app.py
```

```bash
cd frontend && npm run dev
```

Optional: disable scheduler in dev

```bash
export DISABLE_SCHEDULER=1
```

## Backend tests

From the **backend** folder (you are already there if your prompt ends with `.../backend$` — do not run `cd backend` again):

```bash
source .venv/bin/activate
pip install -r requirements.txt   # includes APScheduler
python -m pytest tests/test_monitoring.py -v
```

Or, after `pytest.ini` is present:

```bash
pytest tests/test_monitoring.py -v
```

## Manual API checks

1. Register / login and copy JWT.
2. `POST /api/monitoring` — `{ "domain": "github.com", "monitoring_frequency": "daily" }`
3. `GET /api/monitoring` — list domains
4. `POST /api/monitoring/<id>/scan` — manual monitoring scan
5. `GET /api/notifications` — alerts after score/TLS/header/SSL changes
6. `GET /api/notifications/unread-count` — badge count
7. `PUT /api/notifications/<id>/read`
8. `GET /api/monitoring/summary` — dashboard stats
9. `GET /api/monitoring/trends` — chart data

## Frontend

1. Open **Monitoring** — add domain, run scan, change frequency, pause/delete.
2. Navbar bell — unread badge, dropdown, mark read, delete.
3. Dashboard — monitoring summary cards, recent alerts, security trend chart.

## Scheduler

APScheduler runs every 15 minutes (configurable via `MONITOR_SCHEDULER_INTERVAL_MINUTES`). Domains with `next_scan_at <= now` and `is_active=true` are scanned automatically.

## Alert rules

| Condition | Severity |
|-----------|----------|
| SSL ≤ 30 days (first crossing) | Medium |
| SSL ≤ 7 days (first crossing) | High |
| Score drop ≥ 10 points | High |
| Security header removed | Medium |
| TLS 1.3 removed | High |
