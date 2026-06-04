"""Admin analytics, user management, search, and exports."""
from datetime import datetime, timedelta
from io import StringIO
import csv

from sqlalchemy import func, or_

from app.extensions import db
from app.models import (
    AuditLog,
    MonitoringDomain,
    Notification,
    ScanResult,
    SecurityReport,
    User,
    UserRole,
)


def _active_users_query():
    return User.query.filter(User.deleted_at.is_(None))


def get_platform_stats() -> dict:
    high_risk = MonitoringDomain.query.filter(
        MonitoringDomain.current_risk_level.isnot(None),
        MonitoringDomain.current_risk_level.ilike("%high%"),
    ).count()
    return {
        "total_users": _active_users_query().count(),
        "total_scans": ScanResult.query.count(),
        "total_reports": SecurityReport.query.count(),
        "total_domains": MonitoringDomain.query.count(),
        "total_notifications": Notification.query.count(),
        "high_risk_domains": high_risk,
    }


def _date_bucket(column, period: str):
    dialect = db.session.get_bind().dialect.name
    if dialect == "sqlite":
        if period == "monthly":
            return func.strftime("%Y-%m", column)
        if period == "weekly":
            return func.strftime("%Y-%W", column)
        return func.date(column)
    if period == "monthly":
        return func.date_format(column, "%Y-%m")
    if period == "weekly":
        return func.date_format(column, "%Y-%u")
    return func.date(column)


def get_analytics(period: str = "daily") -> dict:
    period = period if period in ("daily", "weekly", "monthly") else "daily"
    user_bucket = _date_bucket(User.created_at, period)
    scan_bucket = _date_bucket(ScanResult.scan_date, period)

    user_rows = (
        db.session.query(user_bucket.label("label"), func.count(User.id))
        .filter(User.deleted_at.is_(None))
        .group_by(user_bucket)
        .order_by(user_bucket)
        .limit(30)
        .all()
    )
    scan_rows = (
        db.session.query(scan_bucket.label("label"), func.count(ScanResult.id))
        .group_by(scan_bucket)
        .order_by(scan_bucket)
        .limit(30)
        .all()
    )

    risk_rows = (
        db.session.query(ScanResult.risk_level, func.count(ScanResult.id))
        .filter(ScanResult.risk_level.isnot(None))
        .group_by(ScanResult.risk_level)
        .all()
    )
    risk_distribution = [
        {"name": r[0] or "Unknown", "value": r[1]} for r in risk_rows
    ]

    scores = [
        s[0]
        for s in db.session.query(ScanResult.security_score)
        .filter(ScanResult.security_score.isnot(None))
        .all()
    ]
    buckets = [
        {"range": "0-20", "count": 0},
        {"range": "21-40", "count": 0},
        {"range": "41-60", "count": 0},
        {"range": "61-80", "count": 0},
        {"range": "81-100", "count": 0},
    ]
    for score in scores:
        if score <= 20:
            buckets[0]["count"] += 1
        elif score <= 40:
            buckets[1]["count"] += 1
        elif score <= 60:
            buckets[2]["count"] += 1
        elif score <= 80:
            buckets[3]["count"] += 1
        else:
            buckets[4]["count"] += 1

    return {
        "period": period,
        "user_growth": [{"label": str(r[0]), "count": r[1]} for r in user_rows],
        "scan_activity": [{"label": str(r[0]), "count": r[1]} for r in scan_rows],
        "risk_distribution": risk_distribution,
        "score_distribution": buckets,
    }


def list_users(include_deleted: bool = False) -> list:
    q = User.query
    if not include_deleted:
        q = q.filter(User.deleted_at.is_(None))
    return [u.to_admin_dict() for u in q.order_by(User.created_at.desc()).all()]


def get_user(user_id: int) -> User | None:
    return User.query.filter_by(id=user_id, deleted_at=None).first()


def update_user(admin_id: int, user_id: int, data: dict) -> User:
    user = get_user(user_id)
    if not user:
        raise ValueError("User not found")
    if user.id == admin_id and data.get("role") == "user":
        raise ValueError("You cannot demote your own admin account")

    changes = []
    if "role" in data:
        new_role = data["role"]
        if new_role not in ("user", "admin"):
            raise ValueError("role must be 'user' or 'admin'")
        old_role = user.role.value if isinstance(user.role, UserRole) else user.role
        if old_role != new_role:
            user.role = UserRole.admin if new_role == "admin" else UserRole.user
            changes.append(f"role from {old_role} to {new_role}")

    if "is_active" in data:
        new_active = bool(data["is_active"])
        if user.is_active != new_active:
            user.is_active = new_active
            changes.append("activated" if new_active else "suspended")

    if not changes:
        return user

    from app.services.audit_service import log_admin_action

    log_admin_action(
        admin_id,
        "user.update",
        "user",
        user_id,
        f"Admin updated user {user.email}: {', '.join(changes)}",
    )
    db.session.commit()
    return user


def soft_delete_user(admin_id: int, user_id: int) -> None:
    user = get_user(user_id)
    if not user:
        raise ValueError("User not found")
    if user.id == admin_id:
        raise ValueError("You cannot delete your own account")

    user.deleted_at = datetime.utcnow()
    user.is_active = False

    from app.services.audit_service import log_admin_action

    log_admin_action(
        admin_id,
        "user.delete",
        "user",
        user_id,
        f"Admin soft-deleted user {user.email}",
    )
    db.session.commit()


def get_audit_logs(
    page: int = 1,
    per_page: int = 20,
    action: str | None = None,
    admin_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    q = AuditLog.query.order_by(AuditLog.created_at.desc())
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    if admin_id:
        q = q.filter(AuditLog.admin_id == admin_id)
    if date_from:
        try:
            start = datetime.fromisoformat(date_from.replace("Z", ""))
            q = q.filter(AuditLog.created_at >= start)
        except ValueError:
            pass
    if date_to:
        try:
            end = datetime.fromisoformat(date_to.replace("Z", ""))
            q = q.filter(AuditLog.created_at <= end)
        except ValueError:
            pass

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "logs": [log.to_dict() for log in pagination.items],
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }


def global_search(query: str, limit: int = 10) -> dict:
    q = f"%{query.strip()}%"
    users = (
        _active_users_query()
        .filter(or_(User.full_name.ilike(q), User.email.ilike(q)))
        .limit(limit)
        .all()
    )
    scans = (
        ScanResult.query.filter(
            or_(ScanResult.url.ilike(q), ScanResult.domain.ilike(q))
        )
        .order_by(ScanResult.scan_date.desc())
        .limit(limit)
        .all()
    )
    reports = (
        SecurityReport.query.filter(SecurityReport.report_name.ilike(q))
        .order_by(SecurityReport.created_at.desc())
        .limit(limit)
        .all()
    )
    domains = (
        MonitoringDomain.query.filter(MonitoringDomain.domain.ilike(q))
        .limit(limit)
        .all()
    )
    return {
        "users": [u.to_admin_dict() for u in users],
        "scans": [s.to_summary() for s in scans],
        "reports": [
            {
                "id": r.id,
                "report_name": r.report_name,
                "scan_id": r.scan_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ],
        "domains": [d.to_dict() for d in domains],
    }


def get_recent_activity() -> dict:
    return {
        "users": [u.to_admin_dict() for u in _active_users_query().order_by(User.created_at.desc()).limit(5)],
        "scans": [s.to_summary() for s in ScanResult.query.order_by(ScanResult.scan_date.desc()).limit(5)],
        "reports": [
            {
                "id": r.id,
                "report_name": r.report_name,
                "scan_id": r.scan_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in SecurityReport.query.order_by(SecurityReport.created_at.desc()).limit(5)
        ],
        "alerts": [
            n.to_dict()
            for n in Notification.query.order_by(Notification.created_at.desc()).limit(5)
        ],
    }


def get_system_health() -> dict:
    db_ok = True
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        db_ok = False

    from app.services.scheduler_service import scheduler

    monitoring_ok = scheduler is not None and scheduler.running
    return {
        "database": "Healthy" if db_ok else "Unhealthy",
        "api": "Healthy",
        "monitoring_service": "Healthy" if monitoring_ok else "Idle",
    }


def export_users_csv() -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "full_name", "email", "role", "status", "created_at"])
    for u in User.query.order_by(User.id).all():
        status = "deleted" if u.is_deleted else ("active" if u.is_active else "suspended")
        writer.writerow(
            [
                u.id,
                u.full_name,
                u.email,
                u.role.value if isinstance(u.role, UserRole) else u.role,
                status,
                u.created_at.isoformat() if u.created_at else "",
            ]
        )
    return output.getvalue()


def export_scans_csv() -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "user_id", "url", "domain", "security_score", "risk_level", "scan_date"]
    )
    for s in ScanResult.query.order_by(ScanResult.scan_date.desc()).all():
        writer.writerow(
            [
                s.id,
                s.user_id,
                s.url,
                s.domain,
                s.security_score,
                s.risk_level,
                s.scan_date.isoformat() if s.scan_date else "",
            ]
        )
    return output.getvalue()


def export_audit_logs_csv() -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "admin_id", "action", "target_type", "target_id", "description", "created_at"]
    )
    for log in AuditLog.query.order_by(AuditLog.created_at.desc()).all():
        writer.writerow(
            [
                log.id,
                log.admin_id,
                log.action,
                log.target_type,
                log.target_id,
                log.description,
                log.created_at.isoformat() if log.created_at else "",
            ]
        )
    return output.getvalue()
