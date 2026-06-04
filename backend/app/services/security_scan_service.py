"""Orchestrates full security scan pipeline."""
from datetime import datetime, timezone
from typing import Any

from app.services.findings_generator import generate_findings
from app.services.header_analyzer import analyze_security_headers
from app.services.score_engine import (
    calculate_security_score,
    score_to_grade,
    score_to_risk_level,
)
from app.services.ssl_analyzer import analyze_ssl
from app.services.tls_analyzer import analyze_tls
from app.utils.url_validator import normalize_and_validate_url


class SecurityScanService:
    """SSL/TLS, headers, scoring, and findings for a target URL."""

    def run_scan(self, url: str) -> dict[str, Any]:
        normalized_url, hostname, domain = normalize_and_validate_url(url)
        port = 443

        ssl_data = analyze_ssl(hostname, port)
        tls_data = analyze_tls(hostname, port)
        header_data = analyze_security_headers(normalized_url)

        score = calculate_security_score(
            ssl_status=ssl_data.get("ssl_status", "error"),
            tls_versions=tls_data,
            headers=header_data.get("headers", {}),
            days_remaining=ssl_data.get("days_remaining"),
        )

        risk_level = score_to_risk_level(score)
        grade = score_to_grade(score)
        findings = generate_findings(ssl_data, tls_data, header_data, score)

        tls_version = tls_data.get("highest_version") or ssl_data.get(
            "tls_version_detected"
        )

        return {
            "url": normalized_url,
            "domain": domain,
            "ssl_status": ssl_data.get("ssl_status"),
            "issuer": ssl_data.get("issuer"),
            "common_name": ssl_data.get("common_name"),
            "organization": ssl_data.get("organization"),
            "serial_number": ssl_data.get("serial_number"),
            "signature_algorithm": ssl_data.get("signature_algorithm"),
            "certificate_version": ssl_data.get("certificate_version"),
            "public_key_algorithm": ssl_data.get("public_key_algorithm"),
            "domain_name": ssl_data.get("domain_name") or domain,
            "valid_from": ssl_data.get("valid_from"),
            "valid_to": ssl_data.get("valid_to"),
            "days_remaining": ssl_data.get("days_remaining"),
            "tls_version": tls_version,
            "tls_versions": {
                "tls_1_0": tls_data.get("tls_1_0", False),
                "tls_1_1": tls_data.get("tls_1_1", False),
                "tls_1_2": tls_data.get("tls_1_2", False),
                "tls_1_3": tls_data.get("tls_1_3", False),
            },
            "certificate_chain": ssl_data.get("certificate_chain", {}),
            "security_headers": header_data.get("headers", {}),
            "header_values": header_data.get("header_values", {}),
            "security_score": score,
            "risk_level": risk_level,
            "grade": grade,
            "findings": findings,
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "raw_ssl_error": ssl_data.get("error"),
            "raw_header_error": header_data.get("error"),
        }
