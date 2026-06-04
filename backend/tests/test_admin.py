"""Phase 5 admin API tests."""
import os

import pytest

os.environ["FLASK_ENV"] = "testing"

from app import create_app
from app.extensions import db
from app.models import AuditLog, User, UserRole
from tests.conftest import assert_api_error, assert_api_success


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _create_admin():
    admin = User(full_name="Admin", email="admin@securescan.test", role=UserRole.admin)
    admin.set_password("Admin12345!")
    db.session.add(admin)
    db.session.commit()
    return admin


def _token(client, email, password):
    login = assert_api_success(
        client.post("/api/auth/login", json={"email": email, "password": password})
    )
    return login["access_token"]


def test_non_admin_blocked(client, app):
    with app.app_context():
        user = User(full_name="User", email="user@test.com", role=UserRole.user)
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()

    token = _token(client, "user@test.com", "Password123!")
    assert_api_error(
        client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"}),
        403,
    )


def test_admin_stats_and_user_management(client, app):
    with app.app_context():
        admin = _create_admin()
        user = User(full_name="Target", email="target@test.com", role=UserRole.user)
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        admin_id = admin.id

    token = _token(client, "admin@securescan.test", "Admin12345!")

    data = assert_api_success(
        client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    )
    assert "total_users" in data

    assert_api_success(
        client.put(
            f"/api/admin/users/{user_id}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )
    )

    with app.app_context():
        assert AuditLog.query.filter_by(admin_id=admin_id).count() >= 1

    assert_api_error(
        client.post(
            "/api/auth/login",
            json={"email": "target@test.com", "password": "Password123!"},
        ),
        403,
    )


def test_soft_delete_user(client, app):
    with app.app_context():
        _create_admin()
        user = User(full_name="Del", email="del@test.com", role=UserRole.user)
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    token = _token(client, "admin@securescan.test", "Admin12345!")
    assert_api_success(
        client.delete(
            f"/api/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
    )

    with app.app_context():
        deleted = db.session.get(User, user_id)
        assert deleted.deleted_at is not None


def test_audit_logs_pagination(client, app):
    with app.app_context():
        admin = _create_admin()
        db.session.add(
            AuditLog(
                admin_id=admin.id,
                action="test.action",
                target_type="user",
                target_id="1",
                description="Test audit entry",
            )
        )
        db.session.commit()

    token = _token(client, "admin@securescan.test", "Admin12345!")
    data = assert_api_success(
        client.get("/api/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    )
    assert data["total"] >= 1
    assert len(data["logs"]) >= 1
