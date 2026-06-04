"""AI auditor unit tests."""
from app.services.ai_auditor import AIAuditor


def test_ai_auditor_generates_summary_and_recommendations():
    scan = {
        "domain": "example.com",
        "url": "https://example.com",
        "ssl_status": "valid",
        "security_score": 75,
        "risk_level": "Medium Risk",
        "days_remaining": 90,
        "tls_versions": {"tls_1_2": True, "tls_1_3": True, "tls_1_0": False, "tls_1_1": False},
        "security_headers": {
            "hsts": False,
            "csp": False,
            "x_frame_options": True,
            "x_content_type_options": True,
            "referrer_policy": False,
            "permissions_policy": False,
        },
        "findings": [],
    }
    result = AIAuditor().analyze(scan)
    assert "security_summary" in result
    assert len(result["security_summary"]) > 20
    assert result["risk_assessment"]["risk_level"] in ("Low", "Medium", "High")
    assert any(r["priority"] == "High" for r in result["recommendations"])
    assert any(r["title"] == "Enable HSTS" for r in result["recommendations"])
