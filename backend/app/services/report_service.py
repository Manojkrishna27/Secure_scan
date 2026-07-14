"""Report generation orchestration."""
import os
from datetime import datetime

from flask import current_app

from app.extensions import db
from app.models import ScanResult, SecurityReport
from app.services.ai_auditor import AIAuditor
from app.services.pdf_generator import PDFGenerator


def ensure_ai_audit(scan: ScanResult) -> dict:
    """Run AI auditor (Gemini or rule-based fallback) if not already stored on scan."""
    if scan.ai_summary and scan.ai_recommendations:
        return {
            "security_summary": scan.ai_summary,
            "risk_assessment": scan.ai_risk_assessment or {},
            "recommendations": scan.ai_recommendations or [],
        }
    api_key = current_app.config.get("GEMINI_API_KEY", "")
    ai = AIAuditor(api_key=api_key).analyze(scan.to_detail())
    scan.apply_ai_audit(ai)
    db.session.commit()
    return ai


def generate_pdf_report(scan: ScanResult, user_id: int) -> SecurityReport:
    """Generate PDF and persist SecurityReport row."""
    ai = ensure_ai_audit(scan)
    scan_detail = scan.to_detail()

    storage_root = current_app.config["REPORTS_STORAGE_PATH"]
    user_dir = os.path.join(storage_root, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{scan.id}_{timestamp}.pdf"
    filepath = os.path.join(user_dir, filename)

    PDFGenerator(filepath).generate(scan_detail, ai)

    report_name = f"SecureScan - {scan.domain} - {timestamp}.pdf"
    report = SecurityReport(
        user_id=user_id,
        scan_id=scan.id,
        report_name=report_name,
        report_path=filepath,
    )
    db.session.add(report)
    db.session.commit()
    return report
