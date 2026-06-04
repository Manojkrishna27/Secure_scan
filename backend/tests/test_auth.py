"""Authentication API tests (uses in-memory SQLite)."""
import os

import pytest

os.environ["FLASK_ENV"] = "testing"

from app import create_app
from app.extensions import db
from app.models import User, UserRole
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


def test_register_and_login(client):
    r = client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )
    assert_api_success(r, 201)

    r = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    data = assert_api_success(r)
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_protected_me(client):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Me User",
            "email": "me@example.com",
            "password": "Password123",
        },
    )
    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": "me@example.com", "password": "Password123"},
        )
    )
    token = login["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    data = assert_api_success(r)
    assert data["user"]["full_name"] == "Me User"


def test_admin_only(client, app):
    with app.app_context():
        admin = User(
            full_name="Admin",
            email="admin@test.com",
            role=UserRole.admin,
        )
        admin.set_password("Admin12345")
        db.session.add(admin)
        db.session.commit()

    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "Admin12345"},
        )
    )

    r = client.get(
        "/api/admin/admin-only",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    body = r.get_json()
    assert body["success"] is True


def test_logout_revokes_token(client):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Logout User",
            "email": "logout@example.com",
            "password": "Password123",
        },
    )
    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": "logout@example.com", "password": "Password123"},
        )
    )
    token = login["access_token"]

    assert_api_success(
        client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    )

    assert_api_error(
        client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}),
        401,
    )
