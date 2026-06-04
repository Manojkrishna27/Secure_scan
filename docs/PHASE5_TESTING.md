# Phase 5 Testing

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
flask db upgrade
pytest tests/test_admin.py -v
```

## Manual checks

1. Promote a user to `admin` in the database.
2. Log in — open `/admin`, `/admin/users`, `/admin/analytics`, `/admin/logs`.
3. As a normal user, confirm `/admin` redirects to dashboard and `/api/admin/stats` returns 403.
4. Suspend a user — confirm login returns 403.
5. Change a role — confirm audit log entry appears.
6. Export CSV from admin overview.
7. Run global search from admin overview.
