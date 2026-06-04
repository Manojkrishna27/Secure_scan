"""Unit tests for scan engine components."""
import pytest

from app.services.findings_generator import generate_findings
from app.services.ssl_analyzer import _format_cert_dict, _parse_name_tuple
from app.services.score_engine import (
    calculate_security_score,
    score_to_grade,
    score_to_risk_level,
)
from app.utils.url_validator import normalize_and_validate_url


def test_score_calculation_max():
    score = calculate_security_score(
        ssl_status="valid",
        tls_versions={"tls_1_3": True, "tls_1_2": False},
        headers={
            "hsts": True,
            "csp": True,
            "x_frame_options": True,
            "x_content_type_options": True,
            "referrer_policy": True,
            "permissions_policy": True,
        },
        days_remaining=90,
    )
    assert score == 90  # 30 SSL + 20 TLS1.3 + 30 headers + 10 cert days
    assert score_to_risk_level(score) == "Low Risk"
    assert score_to_grade(score) == "A-"


def test_score_high_risk():
    score = calculate_security_score(
        ssl_status="expired",
        tls_versions={"tls_1_0": True, "tls_1_3": False, "tls_1_2": False},
        headers={},
        days_remaining=5,
    )
    assert score < 70
    assert score_to_risk_level(score) == "High Risk"


def test_findings_missing_csp():
    findings = generate_findings(
        {"ssl_status": "valid", "days_remaining": 60},
        {"tls_1_2": True, "tls_1_3": True, "insecure_enabled": []},
        {"headers": {"csp": False, "hsts": True}},
        75,
    )
    titles = [f["title"] for f in findings]
    assert any("Content Security Policy" in t for t in titles)


def test_url_blocks_localhost():
    with pytest.raises(ValueError, match="localhost"):
        normalize_and_validate_url("https://localhost")


def test_url_blocks_private_ip():
    with pytest.raises(ValueError, match="private"):
        normalize_and_validate_url("https://192.168.1.1")


def test_parse_name_tuple_from_getpeercert():
    """ssl.getpeercert() returns (oid_name, value) tuples, not .oid objects."""
    subject = (
        (("countryName", "US"),),
        (("organizationName", "Meta"),),
        (("commonName", "web.whatsapp.com"),),
    )
    parsed = _parse_name_tuple(subject)
    assert parsed["commonName"] == "web.whatsapp.com"
    assert parsed["organizationName"] == "Meta"

    cert_dict = {
        "subject": subject,
        "issuer": ((("commonName", "DigiCert"),),),
        "notBefore": "Jan  1 00:00:00 2026 GMT",
        "notAfter": "Dec 31 23:59:59 2027 GMT",
        "serialNumber": "123",
    }
    formatted = _format_cert_dict(cert_dict)
    assert formatted["common_name"] == "web.whatsapp.com"
    assert formatted["ssl_status"] == "valid"


def test_url_normalizes(monkeypatch):
    monkeypatch.setattr(
        "app.utils.url_validator._resolve_host_ips",
        lambda _h: ["93.184.216.34"],
    )
    url, host, domain = normalize_and_validate_url("example.com")
    assert url == "https://example.com"
    assert host == "example.com"
    assert domain == "example.com"
