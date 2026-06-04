"""Security scan routes."""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db, limiter
from app.models import ScanResult
from app.services.scan_pipeline import run_scan_and_save
from app.utils.api_errors import log_and_message
from app.utils.app_logging import get_logger
from app.utils.responses import api_error, api_success

scan_bp = Blueprint("scans", __name__, url_prefix="/api/scans")
scan_log = get_logger("securescan.scan")


def _current_user_id() -> int:
    return int(get_jwt_identity())


@scan_bp.post("")
@jwt_required()
@limiter.limit("30 per hour")
def start_scan():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if not url:
        return api_error("URL is required", 400)

    try:
        scan, _ = run_scan_and_save(_current_user_id(), url)
        scan_log.info("Scan completed user_id=%s scan_id=%s", _current_user_id(), scan.id)
    except ValueError as exc:
        scan_log.warning("Scan validation failed: %s", exc)
        return api_error(str(exc), 400)
    except Exception as exc:
        scan_log.error("Scan failed for user_id=%s", _current_user_id())
        return api_error(
            log_and_message(exc, user_message="Scan failed. Please try again later."),
            500,
        )

    return api_success(
        data={"scan": scan.to_detail()},
        message="Scan completed successfully",
        status=201,
    )


@scan_bp.get("")
@jwt_required()
def list_scans():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 50, type=int), 100)
    page = max(page, 1)

    pagination = (
        ScanResult.query.filter_by(user_id=_current_user_id())
        .order_by(ScanResult.scan_date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return api_success(
        data={
            "scans": [s.to_summary() for s in pagination.items],
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@scan_bp.get("/<int:scan_id>")
@jwt_required()
def get_scan(scan_id):
    scan = ScanResult.query.filter_by(
        id=scan_id, user_id=_current_user_id()
    ).first()
    if not scan:
        return api_error("Scan not found", 404)
    return api_success(data={"scan": scan.to_detail()})


@scan_bp.delete("/<int:scan_id>")
@jwt_required()
def delete_scan(scan_id):
    scan = ScanResult.query.filter_by(
        id=scan_id, user_id=_current_user_id()
    ).first()
    if not scan:
        return api_error("Scan not found", 404)
    db.session.delete(scan)
    db.session.commit()
    return api_success(message="Scan deleted successfully")
