# SecureScan AI

**Intelligent Website Security Assessment Platform**

SecureScan AI helps teams assess website security through SSL/TLS analysis, security headers, certificate chain validation, scoring, AI recommendations, PDF reports, and domain monitoring.

> **Phase 5** — Admin dashboard, analytics, audit logs, RBAC, rate limiting, CSV exports.

---

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| **Frontend** | React (JSX), Vite, Tailwind CSS, Shadcn/UI, Framer Motion, Axios, React Router, Recharts |
| **Backend** | Python Flask, Flask-JWT-Extended, Flask-Bcrypt, Flask-CORS, SQLAlchemy, Flask-Migrate |
| **Database** | MySQL |
| **Auth (Phase 1+)** | JWT + bcrypt |

---

## Folder Structure

```text
Secure_scan/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/       # Navbar, Sidebar, Footer, Shadcn UI
│   │   ├── pages/
│   │   │   ├── Landing/
│   │   │   ├── Auth/
│   │   │   ├── Dashboard/
│   │   │   └── Admin/
│   │   ├── layouts/
│   │   ├── routes/
│   │   ├── services/         # Axios API client
│   │   ├── context/          # Theme (dark/light)
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── config/
│   │   ├── models/
│   │   ├── routes/           # auth, scan, report, admin, health
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── utils/
│   │   └── __init__.py       # App factory
│   ├── migrations/           # Alembic
│   ├── app.py                # Run: python app.py
│   ├── wsgi.py               # Gunicorn / Docker
│   └── requirements.txt
│
├── docker-compose.yml        # Optional: MySQL, Redis, full stack
└── README.md
```

---

## Prerequisites

- **Node.js** 20+
- **Python** 3.11+
- **MySQL** 8+ (optional for Phase 0 health check; required for DB migrations)

---

## Installation

### 1. Clone and configure environment

```bash
cd Secure_scan
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=securescan
JWT_SECRET_KEY=change_me
```

Create the database:

```sql
CREATE DATABASE securescan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLASK_APP=app:create_app    # for migrations
flask db upgrade                   # optional if MySQL is running
```

### 3. Frontend

```bash
cd frontend
npm install
```

---

## Running the Application

### Backend

```bash
cd backend
source .venv/bin/activate
python app.py
```

API: http://localhost:5000  
Health: http://localhost:5000/api/health

```json
{
  "status": "healthy",
  "service": "SecureScan AI"
}
```

### Frontend

```bash
cd frontend
npm run dev
```

App: http://localhost:5173

The landing page calls `/api/health` (proxied to the backend in dev).

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `MYSQL_HOST` | MySQL host |
| `MYSQL_PORT` | MySQL port (default `3306`) |
| `MYSQL_USER` | Database user |
| `MYSQL_PASSWORD` | Database password |
| `MYSQL_DB` | Database name |
| `JWT_SECRET_KEY` | JWT signing key (Phase 1+) |
| `SECRET_KEY` | Flask session secret |
| `CORS_ORIGINS` | Allowed frontend origins |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend URL (default `http://localhost:5000`) |

---

## API Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/register` | No | Register user |
| POST | `/api/auth/login` | No | Login, returns JWT |
| GET | `/api/auth/me` | Yes | Current user |
| PUT | `/api/auth/profile` | Yes | Update full name |
| PUT | `/api/auth/change-password` | Yes | Change password |
| POST | `/api/auth/logout` | Yes | Revoke JWT (blocklist) |
| GET | `/api/admin/admin-only` | Admin | Admin-only sample route |
| POST | `/api/scans` | Yes | Run security scan |
| GET | `/api/scans` | Yes | Scan history |
| GET | `/api/scans/:id` | Yes | Scan detail |
| DELETE | `/api/scans/:id` | Yes | Delete scan |
| GET | `/api/reports/` | — | Placeholder (Phase 5) |

See [docs/PHASE1_TESTING.md](docs/PHASE1_TESTING.md) for curl examples and UI walkthrough.

---

## Frontend Routes

| Path | Page |
|------|------|
| `/` | Landing |
| `/login` | Login (placeholder) |
| `/register` | Register (placeholder) |
| `/dashboard` | Dashboard |
| `/scan/:id` | Scan details |
| `/reports` | Reports |
| `/settings` | Settings |
| `/admin` | Admin dashboard |

---

## Docker (optional)

```bash
cp .env.example .env
docker compose up --build
```

---

## Development Roadmap

| Phase | Focus |
|-------|--------|
| 0 | Foundation (current) |
| 1 | JWT authentication |
| 2 | SSL/TLS scan engine |
| 3 | Scan UX |
| 4 | AI recommendations |
| 5 | PDF reports |
| 6 | Domain monitoring |
| 7 | Admin dashboard |
| 8 | Production hardening |

---

## License

Proprietary — SecureScan AI. All rights reserved.
