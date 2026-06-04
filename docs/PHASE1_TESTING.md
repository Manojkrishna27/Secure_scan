# Phase 1 — Authentication Testing Guide

## Prerequisites

```bash
# MySQL database created
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS securescan;"

cd backend
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app:create_app
flask db upgrade
python ../scripts/seed_admin.py   # optional: admin@securescan.ai / Admin12345

python app.py
```

```bash
cd frontend
npm run dev
```

---

## 1. User Registration

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Manojkrishna",
    "email": "test@gmail.com",
    "password": "Password123"
  }'
```

**Expected:** `201` — `{"message": "User registered successfully"}`

**Validation tests:**

- Duplicate email → `409`
- Password &lt; 8 chars → `400`
- Missing full name → `400`

---

## 2. User Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gmail.com",
    "password": "Password123"
  }'
```

**Expected:** `200` with `access_token` and `user` object.

Save token:

```bash
export TOKEN="<access_token>"
```

---

## 3. Protected Routes

Without token:

```bash
curl http://localhost:5000/api/auth/me
```

**Expected:** `401`

With token:

```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** `200` with user profile.

**Frontend:** Visit http://localhost:5173/dashboard while logged out → redirects to `/login`.

---

## 4. Admin Route Access

As regular user (`role: user`):

```bash
curl http://localhost:5000/api/admin/admin-only \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** `403` — Admin access required

As admin (after `seed_admin.py`):

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@securescan.ai","password":"Admin12345"}'

export ADMIN_TOKEN="<access_token>"

curl http://localhost:5000/api/admin/admin-only \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected:** `200` — `{"message": "Admin Access Granted"}`

**Frontend:** Admin page → “Test admin route” button.

---

## 5. Logout Flow

```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** `200` — Logged out successfully

Reuse same token on `/api/auth/me`:

**Expected:** `401` — Token has been revoked

**Frontend:** Click Logout → redirected to login; dashboard blocked.

---

## Additional Endpoints

### Update profile

```bash
curl -X PUT http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Updated Name"}'
```

### Change password

```bash
curl -X PUT http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Password123",
    "new_password": "NewPassword123"
  }'
```

---

## UI Walkthrough

1. **Register** at `/register` → success message → `/login`
2. **Login** → redirect to `/dashboard` → “Welcome, {name}” + role
3. **Navbar** shows Dashboard, Reports, Settings, Logout
4. **Settings** → update name / change password
5. **Admin** (admin user only) → test admin API button
6. **Logout** → navbar shows Login / Register
