# 🛡️ SecureScan AI

### Intelligent Website Security Assessment Platform

SecureScan AI is a full-stack cybersecurity platform that analyzes website security posture through SSL/TLS inspection, security header auditing, certificate validation, risk scoring, AI-powered recommendations, PDF reporting, and continuous domain monitoring.

---

## 🌟 Project Highlights

* Full-Stack React + Flask Architecture
* JWT Authentication & Role-Based Access Control (RBAC)
* SSL/TLS Certificate Analysis Engine
* Security Header Auditing
* AI-Powered Security Recommendations
* Professional PDF Security Reports
* Domain Monitoring & Alerts
* Admin Dashboard & Analytics
* Dockerized Deployment
* MySQL Database Integration

---

## 🚀 Features

### 🔐 Security Analysis

* SSL Certificate Validation
* TLS Version Analysis
* Certificate Chain Verification
* Security Header Inspection
* Risk Assessment & Scoring

### 🤖 AI Security Auditor

* Automated Security Findings
* Risk Classification
* Remediation Recommendations

### 📄 Reporting

* Professional PDF Security Reports
* Security Score Dashboard
* Historical Scan Tracking

### 📡 Monitoring

* Domain Monitoring
* SSL Expiry Alerts
* Security Change Detection
* Notification Center

### 👨‍💼 Administration

* JWT Authentication
* Role-Based Access Control (RBAC)
* Admin Dashboard
* Audit Logs
* Analytics & Insights

---

## 📸 Screenshots

### Landing Page

![Landing Page](docs/screenshot/Landing.png)

### Security Dashboard

![Dashboard](docs/screenshot/Dashboard.png)

### Scan Results

![Scan Results](docs/screenshot/Scan_report.png)

### PDF Report

![PDF Report](docs/screenshot/pdf_page1.png)

![PDF Report](docs/screenshot/pdf_report.png)

![PDF Report](docs/screenshot/security_findings.png)

**---**

---

## 🏗️ System Architecture

```text
React Frontend
       │
       ▼
 Flask REST API
       │
       ▼
    MySQL
       │
       ▼
 Security Analysis Engine
 ┌─────────┬─────────┬─────────┐
 │         │         │         │
 ▼         ▼         ▼         ▼
SSL      TLS     Headers    Score
                       │
                       ▼
               AI Recommendation Engine
                       │
                       ▼
                PDF Reporting
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* Vite
* Tailwind CSS
* Shadcn/UI
* Framer Motion
* Axios
* React Router DOM
* Recharts

### Backend

* Flask
* SQLAlchemy
* Flask-JWT-Extended
* Flask-Bcrypt
* Flask-CORS
* Flask-Migrate

### Database

* MySQL

### Security Libraries

* SSL
* Socket
* Cryptography
* Requests

### DevOps

* Docker
* Docker Compose

---

## 📊 Security Score Calculation

| Security Control            | Points |
| --------------------------- | ------ |
| Valid SSL Certificate       | +30    |
| TLS 1.3 Enabled             | +20    |
| TLS 1.2 Enabled             | +10    |
| Security Headers            | +30    |
| Certificate Valid > 30 Days | +10    |

**Maximum Score: 100**

### Risk Classification

| Score  | Risk Level  |
| ------ | ----------- |
| 90–100 | Low Risk    |
| 70–89  | Medium Risk |
| 0–69   | High Risk   |

---

## 🔑 Core Modules

| Module          | Description                              |
| --------------- | ---------------------------------------- |
| Authentication  | JWT-based user authentication            |
| SSL Scanner     | Certificate validation & expiry analysis |
| TLS Analyzer    | Protocol inspection                      |
| Header Scanner  | Security header verification             |
| AI Auditor      | Risk analysis & recommendations          |
| Monitoring      | Continuous domain monitoring             |
| Reporting       | Professional PDF generation              |
| Admin Dashboard | User management & analytics              |

---

## ⚙️ Installation

### Backend

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python app.py
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## 🔐 Environment Variables

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=<your_password>
MYSQL_DB=securescan

JWT_SECRET_KEY=<your_secret_key>
```

---

## 🐳 Docker Deployment

Start all services:

```bash
docker compose up --build
```

Stop all services:

```bash
docker compose down
```

Services Included:

* React Frontend
* Flask Backend
* MySQL Database

---

## 📚 API Overview

### Authentication

* POST `/api/auth/register`
* POST `/api/auth/login`
* GET `/api/auth/me`
* PUT `/api/auth/profile`
* POST `/api/auth/logout`

### Security Scanning

* POST `/api/scans`
* GET `/api/scans`
* GET `/api/scans/<id>`
* DELETE `/api/scans/<id>`

### Reports

* POST `/api/reports/generate/<scan_id>`
* GET `/api/reports`
* GET `/api/reports/download/<id>`

### Monitoring

* POST `/api/monitoring`
* GET `/api/monitoring`

### Administration

* GET `/api/admin/stats`
* GET `/api/admin/users`
* GET `/api/admin/audit-logs`

---

## 💼 Resume Highlights

* Developed a full-stack cybersecurity platform using React, Flask, MySQL, and Docker.
* Implemented SSL/TLS certificate analysis and security header auditing.
* Built JWT authentication, RBAC authorization, monitoring workflows, and PDF reporting.
* Designed scalable REST APIs and administrative analytics dashboards.

---

## 🎯 Future Enhancements

* GitHub Actions CI/CD Pipeline
* Kubernetes Deployment
* Slack & Email Notifications
* Team Workspaces
* Public API Keys
* Historical Security Trend Analysis
* Enterprise Compliance Reports

---

## 👨‍💻 Author

**Manojkrishna M**

B.Tech – Artificial Intelligence & Data Science

GitHub: https://github.com/Manojkrishna27

LinkedIn: https://www.linkedin.com/in/manoj-krishna-m/

---

## 📄 License

This project is intended for educational, research, and portfolio purposes.

Copyright © Manojkrishna M. All Rights Reserved.

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.
