"""Monitoring and notification API tests."""
import os
from datetime import datetime
from unittest.mock import patch

import pytest

os.environ["FLASK_ENV"] = "testing"

from app import create_app
from app.extensions import db
from app.models import MonitoringDomain, MonitoringHistory, Notification, User, UserRole
from app.services.monitoring_service import MonitoringService
from tests.conftest import assert_api_success


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


def _auth_headers(client):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Monitor User",
            "email": "monitor@example.com",
            "password": "Password123",
        },
    )
    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": "monitor@example.com", "password": "Password123"},
        )
    )
    return {"Authorization": f"Bearer {login['access_token']}"}


MOCK_SCAN = {
    "url": "https://example.com",
    "domain": "example.com",
    "ssl_status": "valid",
    "days_remaining": 25,
    "security_score": 82,
    "risk_level": "Medium",
    "tls_versions": {"tls_1_2": True, "tls_1_3": True},
    "security_headers": {"hsts": True, "csp": True},
}


def test_add_and_list_domains(client):
    headers = _auth_headers(client)
    r = client.post(
        "/api/monitoring",
        json={"domain": "example.com", "monitoring_frequency": "daily"},
        headers=headers,
    )
    data = assert_api_success(r, 201)
    assert data["domain"]["domain"] == "example.com"

    list_data = assert_api_success(client.get("/api/monitoring", headers=headers))
    assert len(list_data["domains"]) == 1


def test_notifications_unread(client):
    headers = _auth_headers(client)
    with client.application.app_context():
        user = User.query.filter_by(email="monitor@example.com").first()
        db.session.add(
            Notification(
                user_id=user.id,
                domain="example.com",
                title="Test",
                message="Alert body",
                severity="High",
                is_read=False,
            )
        )
        db.session.commit()

    count_data = assert_api_success(
        client.get("/api/notifications/unread-count", headers=headers)
    )
    assert count_data["unread_count"] >= 1


def test_compare_score_drop_notification(app):
    with app.app_context():
        user = User(full_name="T", email="t@test.com", role=UserRole.user)
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

        record = MonitoringDomain(
            user_id=user.id,
            domain="example.com",
            monitoring_frequency="daily",
            current_score=95,
            last_days_remaining=90,
            last_tls_versions={"tls_1_3": True, "tls_1_2": True},
            last_security_headers={"csp": True, "hsts": True},
            is_active=True,
        )
        db.session.add(record)
        db.session.commit()

        service = MonitoringService()
        previous = {
            "score": 95,
            "days_remaining": 90,
            "tls_versions": record.last_tls_versions,
            "security_headers": record.last_security_headers,
        }
        new_payload = {
            **MOCK_SCAN,
            "security_score": 82,
            "security_headers": {"hsts": True},
            "tls_versions": {"tls_1_2": True, "tls_1_3": False},
        }
        count = service._compare_and_notify(record, previous, new_payload)
        assert count >= 2

        notes = Notification.query.filter_by(user_id=user.id).all()
        messages = " ".join(n.message for n in notes)
        assert "dropped from 95 to 82" in messages
        assert "TLS 1.3" in messages or "Content-Security-Policy" in messages


@patch("app.services.scan_pipeline.SecurityScanService")
@patch("app.services.scan_pipeline.AIAuditor")
def test_run_scan_stores_history(mock_ai, mock_scan_svc, client, app):
    mock_scan_svc.return_value.run_scan.return_value = MOCK_SCAN
    mock_ai.return_value.analyze.return_value = {
        "security_summary": "ok",
        "risk_assessment": {},
        "recommendations": [],
    }

    headers = _auth_headers(client)
    add = client.post(
        "/api/monitoring",
        json={"domain": "example.com", "monitoring_frequency": "weekly"},
        headers=headers,
    )
    domain_id = assert_api_success(add, 201)["domain"]["id"]

    with app.app_context():
        record = MonitoringDomain.query.get(domain_id)
        record.current_score = 90
        record.last_tls_versions = MOCK_SCAN["tls_versions"]
        record.last_security_headers = MOCK_SCAN["security_headers"]
        record.last_days_remaining = 60
        db.session.commit()

    assert_api_success(
        client.post(f"/api/monitoring/{domain_id}/scan", headers=headers)
    )

    with app.app_context():
        history = MonitoringHistory.query.filter_by(
            monitoring_domain_id=domain_id
        ).all()
        assert len(history) >= 1
