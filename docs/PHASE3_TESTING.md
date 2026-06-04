# Phase 3 — AI Auditor & PDF Reports Testing

## Setup

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
flask db upgrade
python app.py
```

---

## 1. AI recommendations (rule-based)

Run a scan — AI fields are populated automatically:

```bash
curl -X POST http://localhost:5000/api/scans \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'
```

Verify response includes:

- `ai_summary` (string)
- `ai_risk_assessment` (`risk_level`, `summary`)
- `ai_recommendations` (array with `priority`, `title`, `description`)

---

## 2. Generate PDF report

```bash
curl -X POST http://localhost:5000/api/reports/generate/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** `201` with `report` object and file under `backend/storage/reports/<user_id>/`.

---

## 3. List reports

```bash
curl http://localhost:5000/api/reports \
  -H "Authorization: Bearer $TOKEN"
```

---

## 4. Download report

```bash
curl -O -J http://localhost:5000/api/reports/download/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. Delete report

```bash
curl -X DELETE http://localhost:5000/api/reports/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. Access control

Try downloading another user's report ID → **404**.

---

## 7. Unit tests

```bash
python -m pytest tests/test_ai_auditor.py -v
```

---

## 8. UI checklist

- [ ] Scan detail shows **AI security summary** and **AI recommendations**
- [ ] **Generate PDF Report** downloads PDF
- [ ] **Reports** page lists history with download/delete
- [ ] Dashboard shows score trend chart and report count
