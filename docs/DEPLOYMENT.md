# SecureScan AI — Deployment

## Environment variables

| Variable | Description |
|----------|-------------|
| `FLASK_ENV` | `production` for live |
| `FLASK_DEBUG` | `0` in production (default is now `0`) |
| `SECRET_KEY` | Flask secret (≥32 random chars; **required** in production) |
| `JWT_SECRET_KEY` | JWT signing key (≥32 random chars; **required** in production) |
| `MYSQL_PASSWORD` or `DATABASE_URL` | Database credentials (**required** in production) |
| `REDIS_URL` | Rate limit storage (`redis://...`; use in Docker/production) |
| `DATABASE_URL` or `MYSQL_*` | MySQL connection |
| `CORS_ORIGINS` | Frontend origin(s) |
| `DISABLE_SCHEDULER` | `1` to disable monitoring scheduler |
| `MONITOR_SCHEDULER_INTERVAL_MINUTES` | Default `15` |

## Production checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Run `flask db upgrade`
- [ ] Use Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app`
- [ ] Serve frontend static build behind HTTPS reverse proxy
- [ ] Enable MySQL backups
- [ ] Rate limits active (`Flask-Limiter`; disabled only in `TESTING`)
- [ ] Security headers enabled (set automatically on API responses)
- [ ] Do not run Flask debug server in production

## Create first admin

After registering a user, promote in MySQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
```

## Health

- Public: `GET /api/health`
- Admin: `GET /api/admin/health` (JWT + admin)
