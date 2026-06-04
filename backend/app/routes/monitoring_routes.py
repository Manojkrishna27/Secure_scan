"""Domain monitoring API routes."""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db, limiter
from app.models import MonitoringDomain
from app.services.monitoring_service import MonitoringService
from app.utils.api_errors import log_and_message
from app.utils.app_logging import get_logger
from app.utils.responses import api_error, api_success

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/monitoring")
monitor_log = get_logger("securescan.monitoring")


def _current_user_id() -> int:
    return int(get_jwt_identity())


@monitoring_bp.post("")
@jwt_required()
def add_domain():
    data = request.get_json(silent=True) or {}
    domain = (data.get("domain") or "").strip()
    frequency = (data.get("monitoring_frequency") or "daily").strip().lower()

    if not domain:
        return api_error("domain is required", 400)

    try:
        record = MonitoringService().add_domain(
            _current_user_id(), domain, frequency
        )
    except ValueError as exc:
        return api_error(str(exc), 400)

    return api_success(
        data={"domain": record.to_dict()},
        message="Domain added for monitoring",
        status=201,
    )


@monitoring_bp.get("")
@jwt_required()
def list_domains():
    domains = (
        MonitoringDomain.query.filter_by(user_id=_current_user_id())
        .order_by(MonitoringDomain.created_at.desc())
        .all()
    )
    return api_success(data={"domains": [d.to_dict() for d in domains]})


@monitoring_bp.get("/summary")
@jwt_required()
def monitoring_summary():
    summary = MonitoringService().get_summary(_current_user_id())
    return api_success(data=summary)


@monitoring_bp.get("/trends")
@jwt_required()
def monitoring_trends():
    limit = min(request.args.get("limit", 30, type=int), 100)
    trends = MonitoringService().get_trend_data(_current_user_id(), limit=limit)
    return api_success(data={"trends": trends})


@monitoring_bp.put("/<int:domain_id>")
@jwt_required()
def update_domain(domain_id):
    record = MonitoringDomain.query.filter_by(
        id=domain_id, user_id=_current_user_id()
    ).first()
    if not record:
        return api_error("Monitored domain not found", 404)

    data = request.get_json(silent=True) or {}
    if "monitoring_frequency" in data:
        freq = str(data["monitoring_frequency"]).lower()
        if freq not in ("daily", "weekly"):
            return api_error("monitoring_frequency must be daily or weekly", 400)
        record.monitoring_frequency = freq
        if record.last_scan_at:
            record.next_scan_at = record.compute_next_scan_at(record.last_scan_at)

    if "is_active" in data:
        record.is_active = bool(data["is_active"])

    db.session.commit()
    return api_success(
        data={"domain": record.to_dict()},
        message="Monitoring updated",
    )


@monitoring_bp.delete("/<int:domain_id>")
@jwt_required()
def delete_domain(domain_id):
    record = MonitoringDomain.query.filter_by(
        id=domain_id, user_id=_current_user_id()
    ).first()
    if not record:
        return api_error("Monitored domain not found", 404)

    db.session.delete(record)
    db.session.commit()
    return api_success(message="Domain removed from monitoring")


@monitoring_bp.post("/<int:domain_id>/scan")
@jwt_required()
@limiter.limit("30 per hour")
def run_scan(domain_id):
    try:
        result = MonitoringService().run_domain_scan(domain_id, _current_user_id())
        monitor_log.info(
            "Monitoring scan domain_id=%s scan_id=%s",
            domain_id,
            result.get("scan_id"),
        )
    except ValueError as exc:
        return api_error(str(exc), 400)
    except Exception as exc:
        monitor_log.error("Monitoring scan failed domain_id=%s", domain_id)
        return api_error(
            log_and_message(
                exc,
                user_message="Monitoring scan failed. Please try again later.",
            ),
            500,
        )

    return api_success(
        data={
            "scan_id": result["scan_id"],
            "notifications_created": result["notifications_created"],
            "domain": result["domain"],
        },
        message="Monitoring scan completed",
    )
