"""Rule-based AI security auditor — no external APIs."""
from typing import Any


class AIAuditor:
    """Analyze scan results and produce summary, risk assessment, and recommendations."""

    HEADER_LABELS = {
        "hsts": "Strict-Transport-Security (HSTS)",
        "csp": "Content-Security-Policy (CSP)",
        "x_frame_options": "X-Frame-Options",
        "x_content_type_options": "X-Content-Type-Options",
        "referrer_policy": "Referrer-Policy",
        "permissions_policy": "Permissions-Policy",
    }

    def analyze(self, scan_data: dict[str, Any]) -> dict[str, Any]:
        """Return security_summary, risk_assessment, recommendations."""
        recommendations = self._build_recommendations(scan_data)
        risk_assessment = self._build_risk_assessment(scan_data, recommendations)
        security_summary = self._build_summary(scan_data, risk_assessment)

        return {
            "security_summary": security_summary,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
        }

    def _build_summary(self, scan: dict, risk: dict) -> str:
        parts = []
        domain = scan.get("domain") or scan.get("url", "the website")
        ssl = scan.get("ssl_status")
        tls = scan.get("tls_versions") or {}
        score = scan.get("security_score", 0)

        if ssl == "valid":
            parts.append(f"{domain} has a valid SSL certificate")
        elif ssl == "expired":
            parts.append(f"{domain} has an expired SSL certificate")
        else:
            parts.append(f"{domain} has SSL certificate issues")

        tls_bits = []
        if tls.get("tls_1_3"):
            tls_bits.append("TLS 1.3")
        if tls.get("tls_1_2"):
            tls_bits.append("TLS 1.2")
        if tls_bits:
            parts.append(f"and supports {', '.join(tls_bits)}")
        elif ssl == "valid":
            parts.append("but modern TLS support could not be fully verified")

        headers = scan.get("security_headers") or {}
        missing = [k for k, v in headers.items() if not v]
        if missing:
            missing_names = [self.HEADER_LABELS.get(k, k) for k in missing[:3]]
            parts.append(
                f". However, {', '.join(missing_names)}"
                + (" and other headers" if len(missing) > 3 else "")
                + " are missing, which increases potential security risks"
            )
        else:
            parts.append(". Security headers are well configured")

        if tls.get("tls_1_0") or tls.get("tls_1_1"):
            parts.append(". Deprecated TLS 1.0/1.1 protocols may still be enabled")

        days = scan.get("days_remaining")
        if days is not None and days <= 30:
            parts.append(f". The certificate expires in {days} days and should be renewed soon")

        parts.append(
            f". Overall security score is {score}/100 ({risk.get('risk_level', 'Unknown')} risk)."
        )
        return "".join(parts)

    def _build_risk_assessment(
        self, scan: dict, recommendations: list
    ) -> dict[str, str]:
        score = scan.get("security_score") or 0
        high_count = sum(1 for r in recommendations if r["priority"] == "High")

        if score >= 90 and high_count == 0:
            level = "Low"
        elif score >= 70 and high_count <= 1:
            level = "Medium"
        else:
            level = "High"

        summaries = {
            "Low": "Security posture is strong with minor or no critical gaps.",
            "Medium": "Missing security headers or configuration gaps detected.",
            "High": "Critical SSL/TLS or certificate issues require immediate attention.",
        }
        if high_count >= 2:
            summaries["Medium"] = "Multiple high-priority issues detected."
            summaries["High"] = "Severe misconfigurations threaten site security."

        return {
            "risk_level": level,
            "summary": summaries.get(level, summaries["Medium"]),
        }

    def _build_recommendations(self, scan: dict) -> list[dict[str, str]]:
        recs: list[dict[str, str]] = []
        headers = scan.get("security_headers") or {}
        tls = scan.get("tls_versions") or {}
        ssl = scan.get("ssl_status")
        days = scan.get("days_remaining")

        if ssl == "expired":
            recs.append(
                {
                    "priority": "High",
                    "title": "Renew SSL Certificate",
                    "description": "The certificate has expired. Renew immediately to restore HTTPS trust.",
                }
            )
        elif ssl in ("invalid", "error"):
            recs.append(
                {
                    "priority": "High",
                    "title": "Fix SSL Configuration",
                    "description": "Resolve certificate errors so clients can establish secure connections.",
                }
            )

        if days is not None and 0 <= days <= 30:
            recs.append(
                {
                    "priority": "High",
                    "title": "Plan Certificate Renewal",
                    "description": f"Certificate expires in {days} days. Schedule renewal before expiry.",
                }
            )

        if tls.get("tls_1_0") or tls.get("tls_1_1"):
            recs.append(
                {
                    "priority": "High",
                    "title": "Disable Legacy TLS Protocols",
                    "description": "Disable TLS 1.0 and 1.1. Use TLS 1.2 and 1.3 only.",
                }
            )

        if not tls.get("tls_1_2") and not tls.get("tls_1_3"):
            recs.append(
                {
                    "priority": "High",
                    "title": "Enable Modern TLS",
                    "description": "Enable TLS 1.2 and TLS 1.3 on the web server.",
                }
            )

        if not headers.get("hsts"):
            recs.append(
                {
                    "priority": "High",
                    "title": "Enable HSTS",
                    "description": "Prevent protocol downgrade attacks and enforce HTTPS.",
                }
            )

        if not headers.get("csp"):
            recs.append(
                {
                    "priority": "High",
                    "title": "Enable Content Security Policy",
                    "description": "Reduce XSS risks by defining allowed content sources.",
                }
            )

        if not headers.get("x_frame_options"):
            recs.append(
                {
                    "priority": "Medium",
                    "title": "Set X-Frame-Options",
                    "description": "Prevent clickjacking by controlling frame embedding.",
                }
            )

        if not headers.get("x_content_type_options"):
            recs.append(
                {
                    "priority": "Medium",
                    "title": "Set X-Content-Type-Options",
                    "description": "Use nosniff to prevent MIME-type confusion attacks.",
                }
            )

        if not headers.get("referrer_policy"):
            recs.append(
                {
                    "priority": "Low",
                    "title": "Configure Referrer-Policy",
                    "description": "Limit referrer information sent to third parties.",
                }
            )

        if not headers.get("permissions_policy"):
            recs.append(
                {
                    "priority": "Low",
                    "title": "Configure Permissions-Policy",
                    "description": "Restrict browser features such as camera and geolocation.",
                }
            )

        if not tls.get("tls_1_3") and tls.get("tls_1_2"):
            recs.append(
                {
                    "priority": "Medium",
                    "title": "Enable TLS 1.3",
                    "description": "Upgrade to TLS 1.3 for improved performance and security.",
                }
            )

        if (scan.get("security_score") or 0) < 70 and not recs:
            recs.append(
                {
                    "priority": "High",
                    "title": "Improve Overall Security Posture",
                    "description": "Address findings from the scan to raise your security score.",
                }
            )

        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        recs.sort(key=lambda r: priority_order.get(r["priority"], 3))
        return recs
