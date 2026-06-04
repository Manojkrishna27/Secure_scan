"""Generate security findings from scan data."""
from typing import Any


def generate_findings(
    ssl_data: dict,
    tls_data: dict,
    header_data: dict,
    score: int,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    ssl_status = ssl_data.get("ssl_status")
    if ssl_status == "expired":
        findings.append(
            {
                "severity": "Critical",
                "title": "SSL Certificate Expired",
                "recommendation": "Renew the SSL certificate immediately to restore secure connections.",
            }
        )
    elif ssl_status in ("invalid", "error"):
        findings.append(
            {
                "severity": "High",
                "title": "SSL Certificate Invalid or Unreachable",
                "recommendation": ssl_data.get("error")
                or "Fix certificate configuration and ensure HTTPS is properly deployed.",
            }
        )

    days = ssl_data.get("days_remaining")
    if days is not None and 0 <= days <= 30:
        findings.append(
            {
                "severity": "High",
                "title": "SSL Certificate Expiring Soon",
                "recommendation": f"Certificate expires in {days} days. Plan renewal before expiry.",
            }
        )

    for insecure in tls_data.get("insecure_enabled", []):
        label = insecure.replace("_", " ").upper()
        findings.append(
            {
                "severity": "High",
                "title": f"Insecure Protocol Enabled ({label})",
                "recommendation": "Disable TLS 1.0 and TLS 1.1. Use TLS 1.2 or TLS 1.3 only.",
            }
        )

    if not tls_data.get("tls_1_2") and not tls_data.get("tls_1_3"):
        findings.append(
            {
                "severity": "Critical",
                "title": "No Modern TLS Support Detected",
                "recommendation": "Enable TLS 1.2 and TLS 1.3 on the web server.",
            }
        )

    header_map = {
        "csp": (
            "Missing Content Security Policy Header",
            "Enable CSP to reduce XSS attack risks.",
        ),
        "hsts": (
            "Missing Strict-Transport-Security Header",
            "Enable HSTS to enforce HTTPS and prevent downgrade attacks.",
        ),
        "x_frame_options": (
            "Missing X-Frame-Options Header",
            "Set X-Frame-Options to prevent clickjacking attacks.",
        ),
        "x_content_type_options": (
            "Missing X-Content-Type-Options Header",
            "Set X-Content-Type-Options: nosniff to prevent MIME sniffing.",
        ),
        "referrer_policy": (
            "Missing Referrer-Policy Header",
            "Configure Referrer-Policy to control referrer information leakage.",
        ),
        "permissions_policy": (
            "Missing Permissions-Policy Header",
            "Configure Permissions-Policy to restrict browser features.",
        ),
    }

    headers = header_data.get("headers", {})
    for key, (title, recommendation) in header_map.items():
        if not headers.get(key):
            severity = "Medium" if key in ("csp", "hsts") else "Low"
            findings.append(
                {
                    "severity": severity,
                    "title": title,
                    "recommendation": recommendation,
                }
            )

    if header_data.get("error"):
        findings.append(
            {
                "severity": "Medium",
                "title": "HTTP Headers Could Not Be Retrieved",
                "recommendation": header_data["error"],
            }
        )

    if score < 70:
        findings.append(
            {
                "severity": "High",
                "title": "Overall Security Score Below Threshold",
                "recommendation": "Address critical and high severity findings to improve your security posture.",
            }
        )

    return findings
