# Phase 2 — API Samples & Postman

## Postman collection

Import: [`postman/SecureScan-AI.postman_collection.json`](postman/SecureScan-AI.postman_collection.json)

1. Set collection variable `baseUrl` → `http://localhost:5000`
2. Run **Auth → Login** (saves `accessToken` automatically)
3. Run **Scans → Start Scan**

---

## 1. Login (get JWT)

**POST** `/api/auth/login`

```json
{
  "email": "test@gmail.com",
  "password": "Password123"
}
```

**Response 200**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "full_name": "Manojkrishna",
    "email": "test@gmail.com",
    "role": "user"
  }
}
```

Use header: `Authorization: Bearer <access_token>`

---

## 2. Start scan

**POST** `/api/scans`

```json
{
  "url": "https://github.com"
}
```

**Response 201** (abbreviated)

```json
{
  "message": "Scan completed successfully",
  "scan": {
    "id": 1,
    "url": "https://github.com",
    "domain": "github.com",
    "security_score": 85,
    "grade": "B+",
    "risk_level": "Medium Risk",
    "ssl_status": "valid",
    "issuer": "Sectigo ECC Domain Validation Secure Server CA",
    "common_name": "github.com",
    "valid_from": "2025-01-15T00:00:00",
    "valid_to": "2026-02-14T23:59:59",
    "days_remaining": 120,
    "tls_version": "TLSv1.3",
    "tls_versions": {
      "tls_1_0": false,
      "tls_1_1": false,
      "tls_1_2": true,
      "tls_1_3": true
    },
    "certificate_chain": {
      "root_ca": "Sectigo",
      "intermediate_ca": "Sectigo ECC Domain Validation Secure Server CA",
      "end_entity": "github.com"
    },
    "security_headers": {
      "hsts": true,
      "csp": false,
      "x_frame_options": true,
      "x_content_type_options": true,
      "referrer_policy": true,
      "permissions_policy": false
    },
    "findings": [
      {
        "severity": "Medium",
        "title": "Missing Content Security Policy Header",
        "recommendation": "Enable CSP to reduce XSS attack risks."
      }
    ],
    "scan_date": "2026-06-01T12:00:00",
    "created_at": "2026-06-01T12:00:00"
  }
}
```

---

## 3. Scan history

**GET** `/api/scans`

**Response 200**

```json
{
  "scans": [
    {
      "id": 1,
      "url": "https://github.com",
      "domain": "github.com",
      "security_score": 85,
      "risk_level": "Medium Risk",
      "grade": "B+",
      "scan_date": "2026-06-01T12:00:00.000000",
      "ssl_status": "valid"
    }
  ]
}
```

---

## 4. Scan detail

**GET** `/api/scans/1`

Same full `scan` object as start-scan response.

---

## 5. Delete scan

**DELETE** `/api/scans/1`

**Response 200**

```json
{
  "message": "Scan deleted successfully"
}
```

---

## 6. Blocked URL (SSRF protection)

**POST** `/api/scans`

```json
{
  "url": "https://192.168.1.1"
}
```

**Response 400**

```json
{
  "error": "Scanning private or reserved IP addresses is not allowed."
}
```

---

## Database migration

```bash
cd backend
export FLASK_APP=app:create_app
flask db upgrade
```

---

## File map (Phase 2)

| Component | Path |
|-----------|------|
| Model | `backend/app/models/scan_result.py` |
| Migration | `backend/migrations/versions/003_phase2_scan_results.py` |
| URL validation | `backend/app/services/url_validation_service.py` |
| SSL analyzer | `backend/app/services/ssl_analyzer.py` |
| TLS analyzer | `backend/app/services/tls_analyzer.py` |
| Header analyzer | `backend/app/services/header_analyzer.py` |
| Score engine | `backend/app/services/score_engine.py` |
| Findings engine | `backend/app/services/findings_engine.py` |
| Orchestrator | `backend/app/services/security_scan_service.py` |
| APIs | `backend/app/routes/scan_routes.py` |
| Frontend service | `frontend/src/services/scanService.js` |
| Dashboard | `frontend/src/pages/Dashboard/DashboardPage.jsx` |
| Results | `frontend/src/pages/Dashboard/ScanDetailsPage.jsx` |
| History | `frontend/src/pages/Dashboard/ScanHistoryPage.jsx` |
