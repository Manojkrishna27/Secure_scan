# SecureScan AI — Docker Deployment Guide

Run the full stack (MySQL, Redis, Flask API, React frontend) with one command.

## Architecture

```text
Browser → http://localhost:5173 (nginx)
              ├── /        → React static build
              └── /api/*   → proxy → backend:5000
Backend → mysql:3306, redis:6379
```

## Prerequisites

- Docker 24+
- Docker Compose v2

## Quick start

```bash
cd /path/to/Secure_scan

# Use Docker environment (required for compose)
cp .env.docker .env

# Edit secrets before production (SECRET_KEY, JWT_SECRET_KEY)
# python -c "import secrets; print(secrets.token_hex(32))"

docker compose build
docker compose up -d
```

Open:

- **Frontend:** http://localhost:5173  
- **Backend API:** http://localhost:5000/api/health  
- **MySQL (host):** localhost:3307 → container 3306 (avoids conflict with local MySQL on 3306)
- **Redis (host):** localhost:6380 → container 6379

## Run commands

| Action | Command |
|--------|---------|
| Build | `docker compose build` |
| Start (detached) | `docker compose up -d` |
| Start + rebuild | `docker compose up -d --build` |
| Logs (all) | `docker compose logs -f` |
| Logs (backend) | `docker compose logs -f backend` |
| Stop | `docker compose down` |
| Stop + remove DB volume | `docker compose down -v` |
| Status | `docker compose ps` |

## Individual image builds

```bash
docker build -t securescan-frontend ./frontend
docker build -t securescan-backend ./backend
```

## Environment (`.env.docker`)

| Variable | Description |
|----------|-------------|
| `MYSQL_HOST` | `mysql` (Docker service name) |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` / `MYSQL_PASSWORD` | App DB user (created by MySQL image) |
| `MYSQL_ROOT_PASSWORD` | Root password for admin / healthcheck |
| `MYSQL_DB` | Database name (`securescan`) |
| `DATABASE_URL` | SQLAlchemy URL (recommended in Docker) |
| `JWT_SECRET_KEY` | ≥32 chars when `FLASK_ENV=production` |
| `SECRET_KEY` | Flask secret, ≥32 chars in production |
| `REDIS_URL` | `redis://redis:6379/0` |
| `CORS_ORIGINS` | Browser origins (localhost:5173) |
| `VITE_API_BASE_URL` | Leave empty so nginx proxies `/api` |

## Volumes

| Volume | Purpose |
|--------|---------|
| `securescan_mysql_data` | Persistent MySQL data |
| `securescan_backend_reports` | Generated PDF reports |

## Health checks

- **MySQL:** `mysqladmin ping`
- **Redis:** `redis-cli ping`
- **Backend:** `curl http://127.0.0.1:5000/api/health`
- **Frontend:** `wget http://127.0.0.1:5173/`

## Startup verification

1. **Containers healthy**

   ```bash
   docker compose ps
   ```

   All services should show `healthy`.

2. **API health**

   ```bash
   curl -s http://localhost:5000/api/health | jq .
   ```

3. **Frontend**

   Open http://localhost:5173 — landing page loads.

4. **Register / login**

   Create an account via UI or:

   ```bash
   curl -s -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"full_name":"Docker User","email":"docker@test.com","password":"Password123!"}'
   ```

5. **Scan** (with JWT from login)

   Use dashboard URL scan or API `POST /api/scans`.

6. **PDF report**

   Open scan details → **Generate PDF**, or `POST /api/reports/generate/:scan_id`.

7. **Monitoring**

   Add a domain under **Monitoring** (scheduler runs in backend container).

## Create admin user

```bash
docker compose exec backend python /app/../scripts/seed_admin.py
```

Or from host:

```bash
docker compose exec mysql mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" securescan \
  -e "UPDATE users SET role='admin' WHERE email='your@email.com';"
```

## Troubleshooting

### Backend exits on startup

- Check logs: `docker compose logs backend`
- Ensure `SECRET_KEY` and `JWT_SECRET_KEY` are at least 32 characters when `FLASK_ENV=production`.
- Confirm `DATABASE_URL` matches MySQL credentials.

### `flask db upgrade` fails

- Wait for MySQL healthy: `docker compose ps mysql`
- Retry: `docker compose restart backend`

### Frontend shows API errors

- With nginx proxy, `VITE_API_BASE_URL` should be **empty** at build time.
- Rebuild: `docker compose build --no-cache frontend`
- Or set `VITE_API_BASE_URL=http://localhost:5000` and rebuild (calls API directly from browser).

### CORS errors

- Add your origin to `CORS_ORIGINS` in `.env.docker`, e.g. `http://localhost:5173`.

### Redis connection / rate limit

- Ensure `redis` service is healthy.
- Backend falls back to in-memory rate limits if Redis is unreachable at startup.

### Reset everything

```bash
docker compose down -v
docker compose up -d --build
```

## Production notes

- Replace placeholder secrets in `.env.docker`.
- Put TLS termination on a reverse proxy (Traefik, Caddy, nginx).
- Do not expose MySQL/Redis ports publicly in production.
- Increase `GUNICORN_WORKERS` for load.
- Back up volume `securescan_mysql_data` regularly.
