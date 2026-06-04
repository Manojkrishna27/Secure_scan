"""Security report PDF routes."""
import os

from flask import Blueprint, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import ScanResult, SecurityReport
from app.services.report_service import generate_pdf_report
from app.utils.api_errors import log_and_message
from app.utils.app_logging import get_logger
from app.utils.responses import api_error, api_success

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")
report_log = get_logger("securescan.report")


def _current_user_id() -> int:
    return int(get_jwt_identity())


@report_bp.post("/generate/<int:scan_id>")
@jwt_required()
def generate_report(scan_id):
    scan = ScanResult.query.filter_by(
        id=scan_id, user_id=_current_user_id()
    ).first()
    if not scan:
        return api_error("Scan not found", 404)

    try:
        report = generate_pdf_report(scan, _current_user_id())
        report_log.info("PDF generated user_id=%s report_id=%s", _current_user_id(), report.id)
    except Exception as exc:
        report_log.error("PDF generation failed scan_id=%s", scan_id)
        return api_error(
            log_and_message(
                exc,
                user_message="Report generation failed. Please try again later.",
            ),
            500,
        )

    return api_success(
        data={"report": report.to_dict()},
        message="Report generated successfully",
        status=201,
    )


@report_bp.get("")
@jwt_required()
def list_reports():
    reports = (
        SecurityReport.query.filter_by(user_id=_current_user_id())
        .order_by(SecurityReport.created_at.desc())
        .limit(100)
        .all()
    )
    return api_success(data={"reports": [r.to_dict() for r in reports]})


@report_bp.get("/<int:report_id>")
@jwt_required()
def get_report(report_id):
    report = SecurityReport.query.filter_by(
        id=report_id, user_id=_current_user_id()
    ).first()
    if not report:
        return api_error("Report not found", 404)
    return api_success(data={"report": report.to_dict()})


@report_bp.get("/download/<int:report_id>")
@jwt_required()
def download_report(report_id):
    report = SecurityReport.query.filter_by(
        id=report_id, user_id=_current_user_id()
    ).first()
    if not report:
        return api_error("Report not found", 404)

    if not os.path.isfile(report.report_path):
        return api_error("Report file missing on server", 404)

    return send_file(
        report.report_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=report.report_name,
    )


@report_bp.delete("/<int:report_id>")
@jwt_required()
def delete_report(report_id):
    report = SecurityReport.query.filter_by(
        id=report_id, user_id=_current_user_id()
    ).first()
    if not report:
        return api_error("Report not found", 404)

    if os.path.isfile(report.report_path):
        try:
            os.remove(report.report_path)
        except OSError:
            pass

    db.session.delete(report)
    db.session.commit()
    return api_success(message="Report deleted successfully")
