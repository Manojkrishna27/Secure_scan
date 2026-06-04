"""Priority 1 fixes — safe errors, reports, config, rate limits."""
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ["FLASK_ENV"] = "testing"

from app import create_app
from app.extensions import db
from app.models import ScanResult, User, UserRole
from app.models.security_report import SecurityReport
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


def _register_and_token(client, email="flow@test.com"):
    client.post(
        "/api/auth/register",
        json={
            "full_name": "Flow User",
            "email": email,
            "password": "Password123!",
        },
    )
    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": email, "password": "Password123!"},
        )
    )
    return login["access_token"]


def test_report_json_excludes_server_path(client, app):
    token = _register_and_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        user = User.query.filter_by(email="flow@test.com").first()
        scan = ScanResult(
            user_id=user.id,
            url="https://example.com",
            domain="example.com",
            security_score=80,
            risk_level="Low Risk",
        )
        db.session.add(scan)
        db.session.flush()
        report = SecurityReport(
            user_id=user.id,
            scan_id=scan.id,
            report_name="report.pdf",
            report_path="/secret/storage/report.pdf",
        )
        db.session.add(report)
        db.session.commit()
        report_id = report.id

    r = client.get(f"/api/reports/{report_id}", headers=headers)
    data = assert_api_success(r)
    assert "report_path" not in data["report"]
    assert data["report"]["report_name"] == "report.pdf"


@patch("app.services.scan_pipeline.SecurityScanService")
def test_scan_500_hides_internal_error(mock_svc, client):
    mock_svc.return_value.run_scan.side_effect = RuntimeError("secret internal detail")
    token = _register_and_token(client, "scan500@test.com")
    r = client.post(
        "/api/scans",
        json={"url": "https://example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert_api_error(r, 500)
    assert "secret internal detail" not in r.get_json()["message"]


@patch("app.routes.report_routes.generate_pdf_report")
def test_report_generate_safe_error(mock_gen, client, app):
    mock_gen.side_effect = OSError("disk full at /var/secret")
    token = _register_and_token(client, "report500@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        user = User.query.filter_by(email="report500@test.com").first()
        scan = ScanResult(
            user_id=user.id,
            url="https://example.com",
            domain="example.com",
            security_score=70,
        )
        db.session.add(scan)
        db.session.commit()
        scan_id = scan.id

    assert_api_error(
        client.post(f"/api/reports/generate/{scan_id}", headers=headers),
        500,
    )


@patch("app.routes.report_routes.generate_pdf_report")
def test_report_generate_success(mock_gen, client, app):
    token = _register_and_token(client, "reportok@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        user = User.query.filter_by(email="reportok@test.com").first()
        scan = ScanResult(
            user_id=user.id,
            url="https://example.com",
            domain="example.com",
            security_score=90,
        )
        db.session.add(scan)
        db.session.commit()
        scan_id = scan.id

        mock_report = MagicMock()
        mock_report.to_dict.return_value = {
            "id": 99,
            "report_name": "securescan-example.com.pdf",
            "scan_id": scan_id,
        }
        mock_gen.return_value = mock_report

    r = client.post(f"/api/reports/generate/{scan_id}", headers=headers)
    data = assert_api_success(r, 201)
    assert "report_path" not in data["report"]


def test_non_admin_forbidden_message(client, app):
    with app.app_context():
        user = User(full_name="U", email="user403@test.com", role=UserRole.user)
        user.set_password("Password123!")
        db.session.add(user)
        db.session.commit()

    login = assert_api_success(
        client.post(
            "/api/auth/login",
            json={"email": "user403@test.com", "password": "Password123!"},
        )
    )
    assert_api_error(
        client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {login['access_token']}"},
        ),
        403,
    )


def test_ssrf_blocks_localhost(client):
    token = _register_and_token(client, "ssrf@test.com")
    assert_api_error(
        client.post(
            "/api/scans",
            json={"url": "https://localhost"},
            headers={"Authorization": f"Bearer {token}"},
        ),
        400,
    )


def test_production_config_rejects_weak_secrets():
    from flask import Flask

    from app.config import ProductionConfig
    from app.config.validation import validate_config

    os.environ["FLASK_ENV"] = "production"
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    app.config["SECRET_KEY"] = "change_me"
    app.config["JWT_SECRET_KEY"] = "x" * 32
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_config(app)
    os.environ["FLASK_ENV"] = "testing"


def test_rate_limit_storage_falls_back_when_redis_unreachable(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:6399/0")
    application = create_app("testing")
    assert application.config["RATELIMIT_STORAGE_URI"] == "memory://"
