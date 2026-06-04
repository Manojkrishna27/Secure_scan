"""Shared scan + AI persistence pipeline."""
from app.extensions import db
from app.models import ScanResult
from app.services.ai_auditor import AIAuditor
from app.services.security_scan_service import SecurityScanService


def run_scan_and_save(
    user_id: int, url: str, *, commit: bool = True
) -> tuple[ScanResult, dict]:
    """Run security scan, AI analysis, persist. Returns (scan, payload)."""
    payload = SecurityScanService().run_scan(url)
    ai = AIAuditor().analyze(payload)
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
