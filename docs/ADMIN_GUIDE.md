# SecureScan AI — Admin User Guide

## Access

Only users with the **admin** role can open `/admin` and admin APIs. Non-admins receive `403` with `{ "message": "Access denied" }`.

## Admin areas

| Page | Path | Purpose |
|------|------|---------|
| Overview | `/admin` | KPIs, charts, search, exports, system health |
| Analytics | `/admin/analytics` | User growth, scans, risk & score charts |
| Users | `/admin/users` | Roles, suspend/activate, soft delete |
| Audit logs | `/admin/logs` | Filterable admin action history |

## User management

- **Change role** — `user` or `admin` via dropdown.
- **Suspend** — Sets `is_active=false`; login and existing JWTs are blocked.
- **Activate** — Restores access.
- **Delete** — Soft delete (`deleted_at` set); account cannot log in.

All changes are written to **audit_logs**.

## CSV exports

From the admin overview: Users, Scans, Audit logs (requires admin JWT).

## API reference

See [PHASE5_API.md](./PHASE5_API.md).

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md).
