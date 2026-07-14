<div align="center">

# 🛡️ SecureScan AI

### Intelligent Website Security Assessment Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://mysql.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Gemini AI](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

**SecureScan AI** is a full-stack cybersecurity platform that analyzes website security posture through SSL/TLS inspection, security header auditing, certificate validation, AI-powered risk scoring, PDF reporting, and continuous domain monitoring.

[Features](#-features) • [Screenshots](#-screenshots) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Tech Stack](#️-tech-stack)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Security Analysis
- SSL/TLS Certificate Validation & Chain Verification
- TLS Version Inspection (1.0 / 1.1 / 1.2 / 1.3)
- Security Header Auditing (HSTS, CSP, X-Frame-Options, etc.)
- Risk Scoring (0–100) with Grade Classification
- Vulnerability Findings & Severity Tagging

</td>
<td width="50%">

### 🤖 AI-Powered Auditor
- **Gemini 1.5 Flash** integration for context-aware analysis
- Executive-level security summaries for non-technical stakeholders
- Prioritised remediation recommendations (High / Medium / Low)
- Deterministic rule-based fallback (works without API key)

</td>
</tr>
<tr>
<td width="50%">

### 📄 Professional Reporting
- One-click PDF security reports with charts & branding
- Historical scan tracking & comparison
- Downloadable audit trails

</td>
<td width="50%">

### 📡 Monitoring & Alerts
- Continuous domain monitoring with scheduled scans
- SSL expiry alerts & security change detection
- In-app notification centre

</td>
</tr>
<tr>
<td width="50%">

### 👨‍💼 Admin Dashboard
- User management with Role-Based Access Control (RBAC)
- Platform-wide analytics & insights
- Full audit logs for compliance

</td>
<td width="50%">

### 🔑 Authentication
- JWT-based secure authentication
- Refresh token rotation
- Profile & password management

</td>
</tr>
</table>

---

## 📸 Screenshots

### 🏠 Landing Page
![Landing Page](docs/screenshot/Landing.png)

### 📊 Security Dashboard
![Dashboard](docs/screenshot/Dashboard.png)

### 🔍 Scan Results
![Scan Results](docs/screenshot/Scan_report.png)

### 📄 PDF Security Report
![PDF Report](docs/screenshot/pdf_report.png)

![Security Findings](docs/screenshot/security_findings.png)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              React Frontend (Vite)           │
│         Tailwind CSS • Shadcn/UI • Recharts  │
└──────────────────┬──────────────────────────┘
                   │  REST API
┌──────────────────▼──────────────────────────┐
│            Flask REST API (Gunicorn)         │
│     JWT Auth • RBAC • SQLAlchemy ORM        │
└──────┬──────────────────────┬───────────────┘
       │                      │
┌──────▼──────┐    ┌──────────▼──────────────┐
│   MySQL 8   │    │   Security Engine        │
│  (via ORM)  │    │                          │
└─────────────┘    │  SSL ─ TLS ─ Headers     │
                   │         │                │
                   │  Score & Risk Engine     │
                   │         │                │
                   │  ┌──────▼──────────┐     │
                   │  │  AI Auditor     │     │
                   │  │  Gemini 1.5 ↕   │     │
                   │  │  Rule Fallback  │     │
                   │  └──────┬──────────┘     │
                   │         │                │
                   │  PDF Report Generator    │
                   └──────────────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │    Redis (Cache /    │
                   │    Rate Limiting)    │
                   └─────────────────────┘
```

---

## 📊 Security Scoring

| Security Control             | Points |
|------------------------------|--------|
| Valid SSL Certificate        | +30    |
| TLS 1.3 Enabled              | +20    |
| TLS 1.2 Enabled              | +10    |
| Security Headers Present     | +30    |
| Certificate Valid > 30 Days  | +10    |
| **Maximum Score**            | **100**|

| Score  | Grade | Risk Level  |
|--------|-------|-------------|
| 90–100 | A     | 🟢 Low      |
| 70–89  | B     | 🟡 Medium   |
| 0–69   | C/F   | 🔴 High     |

---

## 🚀 Quick Start

### 🐳 Option 1 — Docker (Recommended)

> One command starts everything: MySQL, Redis, Backend, Frontend + Adminer DB UI.

```bash
# 1. Clone the repo
git clone https://github.com/Manojkrishna27/Secure_scan.git
cd Secure_scan

# 2. Copy and configure environment
cp .env.docker .env
# Edit .env → add your GEMINI_API_KEY (optional)

# 3. Start all services
docker compose up --build
```

| Service         | URL                        |
|-----------------|----------------------------|
| 🌐 Frontend     | http://localhost:5173       |
| ⚙️ Backend API  | http://localhost:5000/api   |
| 🗄️ Adminer (DB) | http://localhost:8080       |

```bash
# Stop all services
docker compose down
```

---

### 💻 Option 2 — Local Development

**Prerequisites:** Python 3.11+, Node.js 18+, MySQL 8.0

```bash
# Run both backend + frontend with one script
bash scripts/local_dev.sh
```

Or manually:

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

### 🔐 Environment Variables

Copy `.env.docker` to `.env` and fill in your values:

```env
# Database
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=securescan
MYSQL_PASSWORD=your_db_password
MYSQL_DB=securescan

# Security
SECRET_KEY=your_64_char_hex_secret
JWT_SECRET_KEY=your_64_char_jwt_secret

# AI (optional — enables Gemini-powered analysis)
# Get your free key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

> Generate secure keys with: `python -c "import secrets; print(secrets.token_hex(32))"`

---

### 🗄️ First-Time Database Setup

```bash
# After docker compose up, initialise the database
bash scripts/init_db.sh

# Optional: seed with sample data (users, scans, reports)
docker exec -it securescan-backend python scripts/seed_data.py
```

---

## 🛠️ Tech Stack

| Layer          | Technologies                                                                |
|----------------|-----------------------------------------------------------------------------|
| **Frontend**   | React 18, Vite, Tailwind CSS, Shadcn/UI, Framer Motion, Recharts, Axios    |
| **Backend**    | Flask, SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, Flask-CORS, Gunicorn  |
| **Database**   | MySQL 8.0                                                                   |
| **Cache**      | Redis 7                                                                     |
| **AI**         | Google Gemini 1.5 Flash (`google-generativeai`)                             |
| **Security**   | `ssl`, `socket`, `cryptography`, `requests`                                 |
| **DevOps**     | Docker, Docker Compose, Nginx (reverse proxy)                               |
| **DB Viewer**  | Adminer 4.8                                                                 |

---

## 🔑 Core Modules

| Module            | File                              | Description                                      |
|-------------------|-----------------------------------|--------------------------------------------------|
| AI Auditor        | `services/ai_auditor.py`          | Gemini 1.5 Flash + deterministic rule fallback   |
| SSL Analyzer      | `services/ssl_analyzer.py`        | Certificate validation & expiry analysis         |
| TLS Analyzer      | `services/tls_analyzer.py`        | Protocol version inspection                      |
| Header Analyzer   | `services/header_analyzer.py`     | Security header verification                     |
| Score Engine      | `services/score_engine.py`        | Weighted security score calculation              |
| Monitoring        | `services/monitoring_service.py`  | Scheduled continuous domain monitoring           |
| PDF Generator     | `services/pdf_generator.py`       | Professional report generation with charts       |
| Admin Service     | `services/admin_service.py`       | User management & platform analytics             |

---

## 📚 API Reference

### Authentication
| Method | Endpoint              | Description        |
|--------|-----------------------|--------------------|
| POST   | `/api/auth/register`  | Register new user  |
| POST   | `/api/auth/login`     | Login & get JWT    |
| GET    | `/api/auth/me`        | Get current user   |
| PUT    | `/api/auth/profile`   | Update profile     |
| POST   | `/api/auth/logout`    | Invalidate token   |

### Security Scanning
| Method | Endpoint            | Description          |
|--------|---------------------|----------------------|
| POST   | `/api/scans`        | Run a new scan       |
| GET    | `/api/scans`        | List all scans       |
| GET    | `/api/scans/<id>`   | Get scan details     |
| DELETE | `/api/scans/<id>`   | Delete a scan        |

### Reports
| Method | Endpoint                          | Description          |
|--------|-----------------------------------|----------------------|
| POST   | `/api/reports/generate/<scan_id>` | Generate PDF report  |
| GET    | `/api/reports`                    | List all reports     |
| GET    | `/api/reports/download/<id>`      | Download PDF         |

### Monitoring
| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| POST   | `/api/monitoring` | Add domain to monitoring |
| GET    | `/api/monitoring` | List monitored domains   |

### Administration *(Admin role required)*
| Method | Endpoint                  | Description            |
|--------|---------------------------|------------------------|
| GET    | `/api/admin/stats`        | Platform statistics    |
| GET    | `/api/admin/users`        | Manage users           |
| GET    | `/api/admin/audit-logs`   | View audit trail       |

---

## 🔭 Roadmap

- [ ] GitHub Actions CI/CD Pipeline
- [ ] Email & Slack Notifications
- [ ] Team Workspaces & Shared Reports
- [ ] Historical Security Trend Analysis
- [ ] Public API Key System
- [ ] Kubernetes Deployment Manifests
- [ ] Enterprise Compliance Reports (SOC2, ISO 27001)

---

## 💼 About the Author

**Manojkrishna M**
B.Tech – Artificial Intelligence & Data Science

[![GitHub](https://img.shields.io/badge/GitHub-Manojkrishna27-181717?style=flat-square&logo=github)](https://github.com/Manojkrishna27)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-manoj--krishna--m-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/manoj-krishna-m/)

---

## 📄 License

This project is intended for **educational, research, and portfolio purposes**.

Copyright © 2026 Manojkrishna M. All Rights Reserved.

---

<div align="center">

⭐ **If you found this project useful, please give it a star!** ⭐

</div>
