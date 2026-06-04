# Phase 2 — Security Scanner Testing

## Setup

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
flask db upgrade
python app.py
```

```bash
cd frontend && npm run dev
```

Login, then use the dashboard or curl with JWT.

---

## 1. Start scan (authenticated)

```bash
TOKEN="<your_access_token>"

curl -X POST http://localhost:5000/api/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

**Verify:** `201`, `scan.security_score`, `scan.findings`, `scan.tls_versions`

---

## 2. SSRF / URL validation

```bash
curl -X POST http://localhost:5000/api/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://127.0.0.1"}'
```

**Expected:** `400` — blocked

```bash
curl -X POST http://localhost:5000/api/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://192.168.1.1"}'
```

**Expected:** `400` — private IP blocked

---

## 3. Scan history

```bash
curl http://localhost:5000/api/scans \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:** Array of scans for current user only.

---

## 4. Scan detail

```bash
curl http://localhost:5000/api/scans/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Verify:** Full report with SSL, TLS, headers, findings, certificate chain.

---

## 5. Delete scan

```bash
curl -X DELETE http://localhost:5000/api/scans/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Unit tests

```bash
cd backend
python -m pytest tests/test_scan_engine.py tests/test_auth.py -v
```

---

## 7. UI checklist

- [ ] Dashboard: enter URL → **Analyze Website** → redirects to results
- [ ] Score card shows score, grade, risk level
- [ ] SSL card shows issuer, CN, dates, days remaining
- [ ] TLS card shows 1.0–1.3 checkmarks
- [ ] Headers table lists HSTS, CSP, etc.
- [ ] Findings show severity badges
- [ ] Scan history lists URL, score, risk, date, view/delete
- [ ] Unauthenticated `/dashboard` redirects to login

---

## Score rules (reference)

| Rule | Points |
|------|--------|
| SSL valid | +30 |
| TLS 1.3 | +20 |
| TLS 1.2 (if no 1.3) | +10 |
| Security headers | up to +30 (5 each) |
| Cert &gt; 30 days | +10 |

| Score | Risk |
|-------|------|
| 90–100 | Low Risk |
| 70–89 | Medium Risk |
| 0–69 | High Risk |
