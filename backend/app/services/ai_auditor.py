"""Gemini-powered AI security auditor with rule-based fallback.

Priority:
  1. If GEMINI_API_KEY is configured → call Gemini 1.5 Flash for a rich,
     context-aware security narrative and structured recommendations.
  2. If the API call fails or the key is missing → fall back to the fast
     deterministic rule engine so the scan pipeline never breaks.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# ── Gemini client (lazy-initialised per request) ──────────────────────────────

def _gemini_client(api_key: str):
    """Return a configured Gemini GenerativeModel, or None if unavailable."""
    try:
        import google.generativeai as genai  # type: ignore[import-untyped]
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini SDK not available: %s", exc)
        return None


# ── Prompt builder ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a senior cybersecurity analyst. You will receive raw
SSL/TLS scan data and return a structured JSON security assessment. Your response
MUST be valid JSON only — no markdown, no backticks, no explanation outside JSON.

JSON schema:
{
  "security_summary": "<2-4 sentence executive summary for non-technical stakeholders>",
  "risk_assessment": {
    "risk_level": "<Low|Medium|High>",
    "summary": "<1-2 sentence technical risk summary>"
  },
  "recommendations": [
    {
      "priority": "<High|Medium|Low>",
      "title": "<short action title>",
      "description": "<clear, actionable remediation step>"
    }
  ]
}

Rules:
- risk_level must be exactly one of: Low, Medium, High
- recommendations must be sorted: High first, then Medium, then Low
- Focus on practical, vendor-agnostic remediation advice
- If the SSL cert is expired or TLS 1.0/1.1 is enabled, that is always High priority
- security_summary should be suitable for a C-suite audience"""


def _build_prompt(scan: dict[str, Any]) -> str:
    headers = scan.get("security_headers") or {}
    tls = scan.get("tls_versions") or {}
    findings = scan.get("findings") or []

    missing_headers = [k for k, v in headers.items() if not v]
    present_headers = [k for k, v in headers.items() if v]
    enabled_tls = [k for k, v in tls.items() if v]
    disabled_tls = [k for k, v in tls.items() if not v]

    scan_summary = {
        "domain": scan.get("domain") or scan.get("url"),
        "url": scan.get("url"),
        "ssl_status": scan.get("ssl_status"),
        "tls_version": scan.get("tls_version"),
        "security_score": scan.get("security_score"),
        "grade": scan.get("grade"),
        "risk_level": scan.get("risk_level"),
        "issuer": scan.get("issuer"),
        "organization": scan.get("organization"),
        "days_remaining": scan.get("days_remaining"),
        "enabled_tls_versions": enabled_tls,
        "disabled_tls_versions": disabled_tls,
        "present_security_headers": present_headers,
        "missing_security_headers": missing_headers,
        "open_findings": [
            {"severity": f.get("severity"), "title": f.get("title")}
            for f in findings[:10]
        ],
    }

    return (
        f"{_SYSTEM_PROMPT}\n\n"
        f"Scan data:\n{json.dumps(scan_summary, indent=2)}"
    )


# ── Gemini analysis ────────────────────────────────────────────────────────────

def _call_gemini(api_key: str, scan: dict[str, Any]) -> dict[str, Any] | None:
    """Call Gemini API and parse the JSON response. Returns None on any failure."""
    model = _gemini_client(api_key)
    if model is None:
        return None

    prompt = _build_prompt(scan)
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "response_mime_type": "application/json",
            },
        )
        raw = response.text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        # Validate required keys
        if all(k in result for k in ("security_summary", "risk_assessment", "recommendations")):
            logger.info("Gemini AI analysis completed for domain=%s", scan.get("domain"))
            return result
        logger.warning("Gemini response missing required keys: %s", list(result.keys()))
        return None
    except json.JSONDecodeError as exc:
        logger.warning("Gemini returned non-JSON response: %s", exc)
        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini API call failed: %s", exc)
        return None


# ── Rule-based fallback ────────────────────────────────────────────────────────

class _RuleEngine:
    """Deterministic rule-based auditor — always works, never calls external APIs."""

    HEADER_LABELS = {
        "hsts": "Strict-Transport-Security (HSTS)",
        "csp": "Content-Security-Policy (CSP)",
        "x_frame_options": "X-Frame-Options",
        "x_content_type_options": "X-Content-Type-Options",
        "referrer_policy": "Referrer-Policy",
        "permissions_policy": "Permissions-Policy",
    }

    def analyze(self, scan: dict[str, Any]) -> dict[str, Any]:
        recommendations = self._build_recommendations(scan)
        risk_assessment = self._build_risk_assessment(scan, recommendations)
        security_summary = self._build_summary(scan, risk_assessment)
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
            parts.append(f" and supports {', '.join(tls_bits)}")
        elif ssl == "valid":
            parts.append(" but modern TLS support could not be fully verified")

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

    def _build_risk_assessment(self, scan: dict, recommendations: list) -> dict[str, str]:
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

        return {"risk_level": level, "summary": summaries.get(level, summaries["Medium"])}

    def _build_recommendations(self, scan: dict) -> list[dict[str, str]]:
        recs: list[dict[str, str]] = []
        headers = scan.get("security_headers") or {}
        tls = scan.get("tls_versions") or {}
        ssl = scan.get("ssl_status")
        days = scan.get("days_remaining")

        if ssl == "expired":
            recs.append({"priority": "High", "title": "Renew SSL Certificate",
                         "description": "The certificate has expired. Renew immediately to restore HTTPS trust."})
        elif ssl in ("invalid", "error"):
            recs.append({"priority": "High", "title": "Fix SSL Configuration",
                         "description": "Resolve certificate errors so clients can establish secure connections."})

        if days is not None and 0 <= days <= 30:
            recs.append({"priority": "High", "title": "Plan Certificate Renewal",
                         "description": f"Certificate expires in {days} days. Schedule renewal before expiry."})

        if tls.get("tls_1_0") or tls.get("tls_1_1"):
            recs.append({"priority": "High", "title": "Disable Legacy TLS Protocols",
                         "description": "Disable TLS 1.0 and 1.1. Use TLS 1.2 and 1.3 only."})

        if not tls.get("tls_1_2") and not tls.get("tls_1_3"):
            recs.append({"priority": "High", "title": "Enable Modern TLS",
                         "description": "Enable TLS 1.2 and TLS 1.3 on the web server."})

        if not headers.get("hsts"):
            recs.append({"priority": "High", "title": "Enable HSTS",
                         "description": "Prevent protocol downgrade attacks and enforce HTTPS."})

        if not headers.get("csp"):
            recs.append({"priority": "High", "title": "Enable Content Security Policy",
                         "description": "Reduce XSS risks by defining allowed content sources."})

        if not headers.get("x_frame_options"):
            recs.append({"priority": "Medium", "title": "Set X-Frame-Options",
                         "description": "Prevent clickjacking by controlling frame embedding."})

        if not headers.get("x_content_type_options"):
            recs.append({"priority": "Medium", "title": "Set X-Content-Type-Options",
                         "description": "Use nosniff to prevent MIME-type confusion attacks."})

        if not headers.get("referrer_policy"):
            recs.append({"priority": "Low", "title": "Configure Referrer-Policy",
                         "description": "Limit referrer information sent to third parties."})

        if not headers.get("permissions_policy"):
            recs.append({"priority": "Low", "title": "Configure Permissions-Policy",
                         "description": "Restrict browser features such as camera and geolocation."})

        if not tls.get("tls_1_3") and tls.get("tls_1_2"):
            recs.append({"priority": "Medium", "title": "Enable TLS 1.3",
                         "description": "Upgrade to TLS 1.3 for improved performance and security."})

        if (scan.get("security_score") or 0) < 70 and not recs:
            recs.append({"priority": "High", "title": "Improve Overall Security Posture",
                         "description": "Address findings from the scan to raise your security score."})

        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        recs.sort(key=lambda r: priority_order.get(r["priority"], 3))
        return recs


# ── Public interface ───────────────────────────────────────────────────────────

_rule_engine = _RuleEngine()


class AIAuditor:
    """Analyze scan results using Gemini AI (with rule-based fallback).

    Usage:
        # With Gemini key from Flask app config:
        ai = AIAuditor(api_key=current_app.config.get("GEMINI_API_KEY"))
        result = ai.analyze(scan_data)

        # Without key (rule-based only):
        ai = AIAuditor()
        result = ai.analyze(scan_data)
    """

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    def analyze(self, scan_data: dict[str, Any]) -> dict[str, Any]:
        """Return security_summary, risk_assessment, recommendations.

        Tries Gemini first if an API key is available; falls back to the
        rule engine on any error.
        """
        if self._api_key:
            result = _call_gemini(self._api_key, scan_data)
            if result:
                return result
            logger.info(
                "Gemini analysis failed for domain=%s — using rule-based fallback.",
                scan_data.get("domain"),
            )

        return _rule_engine.analyze(scan_data)
