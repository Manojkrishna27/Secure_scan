"""Shared scan + AI persistence pipeline."""
import os

from app.extensions import db
from app.models import ScanResult
from app.services.ai_auditor import AIAuditor
from app.services.security_scan_service import SecurityScanService


def run_scan_and_save(
    user_id: int, url: str, *, commit: bool = True, api_key: str = ""
) -> tuple[ScanResult, dict]:
    """Run security scan, AI analysis (Gemini or fallback), persist. Returns (scan, payload)."""
    # Resolve API key: prefer explicit arg, then env var
    resolved_key = api_key or os.getenv("GEMINI_API_KEY", "")

    payload = SecurityScanService().run_scan(url)
    ai = AIAuditor(api_key=resolved_key).analyze(payload)
    payload["ai_summary"] = ai["security_summary"]
    payload["ai_risk_assessment"] = ai["risk_assessment"]
    payload["ai_recommendations"] = ai["recommendations"]

    scan = ScanResult.from_scan_payload(user_id, payload)
    db.session.add(scan)
    if commit:
        db.session.commit()
    else:
        db.session.flush()
    return scan, payload
