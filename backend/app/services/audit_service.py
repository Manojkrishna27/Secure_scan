"""Audit logging for admin actions."""
from app.extensions import db
from app.models import AuditLog


def log_admin_action(
    admin_id: int,
    action: str,
    target_type: str,
    target_id: str | int | None,
    description: str,
) -> AuditLog:
    entry = AuditLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        description=description,
    )
    db.session.add(entry)
    db.session.flush()
    return entry
