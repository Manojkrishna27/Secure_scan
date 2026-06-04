# Phase 5 — Admin API

Base: `/api/admin` — all routes require `Authorization: Bearer <token>` and **admin** role.

## Stats & analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/stats` | Platform KPIs |
| GET | `/analytics?period=daily\|weekly\|monthly` | Chart data |
| GET | `/recent` | Recent users, scans, reports, alerts |
| GET | `/health` | Database / API / monitoring status |

## Users

| Method | Path | Body |
|--------|------|------|
| GET | `/users` | — |
| GET | `/users/:id` | — |
| PUT | `/users/:id` | `{ "role": "admin", "is_active": true }` |
| DELETE | `/users/:id` | Soft delete |

## Audit & search

| Method | Path | Query |
|--------|------|-------|
| GET | `/audit-logs` | `page`, `per_page`, `action`, `admin_id`, `date_from`, `date_to` |
| GET | `/search` | `q` (min 2 chars), `limit` |

## Exports

| Method | Path |
|--------|------|
| GET | `/export/users` |
| GET | `/export/scans` |
| GET | `/export/audit-logs` |

## Example stats response

```json
{
  "total_users": 250,
  "total_scans": 1800,
  "total_reports": 950,
  "total_domains": 120,
  "total_notifications": 40,
  "high_risk_domains": 5
}
```
