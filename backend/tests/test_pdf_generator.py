"""PDF generator unit tests."""
import os
import tempfile

import pytest

from app.services.pdf_generator import PDFGenerator


@pytest.fixture
def sample_scan():
    return {
        "id": 1,
        "user_id": 10,
        "url": "https://example.com",
        "domain": "example.com",
        "scan_date": "2026-06-01T12:00:00",
        "created_at": "2026-06-01T12:00:00",
        "security_score": 78,
        "grade": "B",
        "risk_level": "Medium Risk",
        "ssl_status": "valid",
        "issuer": "Let's Encrypt",
        "common_name": "example.com",
        "organization": "Example Org",
        "domain_name": "example.com",
        "valid_from": "2025-01-01T00:00:00",
        "valid_to": "2026-12-31T23:59:59",
        "days_remaining": 200,
        "serial_number": "ABC123",
        "signature_algorithm": "sha256WithRSAEncryption",
        "certificate_version": "v3",
        "public_key_algorithm": "RSA 2048",
        "tls_version": "TLS 1.3",
        "tls_versions": {
            "tls_1_0": False,
            "tls_1_1": False,
            "tls_1_2": True,
            "tls_1_3": True,
        },
        "certificate_chain": {
            "root_ca": "ISRG Root X1",
            "intermediate_ca": "R3",
            "end_entity": "example.com",
        },
        "security_headers": {
            "hsts": True,
            "csp": False,
            "x_frame_options": True,
            "x_content_type_options": True,
            "referrer_policy": False,
            "permissions_policy": False,
        },
        "header_values": {
            "hsts": "max-age=31536000",
            "x_frame_options": "SAMEORIGIN",
        },
        "findings": [
            {
                "severity": "Medium",
                "title": "Missing Content-Security-Policy",
                "recommendation": "Deploy a strict CSP to mitigate XSS.",
            }
        ],
        "ai_summary": "Overall posture is acceptable with header gaps.",
        "reports": [],
    }


@pytest.fixture
def sample_ai():
    return {
        "security_summary": "Automated assessment summary.",
        "risk_assessment": {
            "risk_level": "Medium",
            "summary": "Address missing CSP and referrer policy.",
        },
        "recommendations": [
            {
                "priority": "High",
                "title": "Enable CSP",
                "description": "Define default-src and script-src directives.",
            }
        ],
    }


def test_pdf_generator_produces_file(sample_scan, sample_ai):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "report.pdf")
        PDFGenerator(path).generate(sample_scan, sample_ai)
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 5000
