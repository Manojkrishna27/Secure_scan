"""Notification API routes."""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import Notification
from app.utils.responses import api_error, api_success

notification_bp = Blueprint(
    "notifications", __name__, url_prefix="/api/notifications"
)


def _current_user_id() -> int:
    return int(get_jwt_identity())


@notification_bp.get("")
@jwt_required()
def list_notifications():
    limit = min(request.args.get("limit", 50, type=int), 100)
    notes = (
        Notification.query.filter_by(user_id=_current_user_id())
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return api_success(data={"notifications": [n.to_dict() for n in notes]})


@notification_bp.get("/unread-count")
@jwt_required()
def unread_count():
    count = Notification.query.filter_by(
        user_id=_current_user_id(), is_read=False
    ).count()
    return api_success(data={"unread_count": count})


@notification_bp.put("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    note = Notification.query.filter_by(
        id=notification_id, user_id=_current_user_id()
    ).first()
    if not note:
        return api_error("Notification not found", 404)

    note.is_read = True
    db.session.commit()
    return api_success(
        data={"notification": note.to_dict()},
        message="Notification marked as read",
    )


@notification_bp.delete("/<int:notification_id>")
@jwt_required()
def delete_notification(notification_id):
    note = Notification.query.filter_by(
        id=notification_id, user_id=_current_user_id()
    ).first()
    if not note:
        return api_error("Notification not found", 404)

    db.session.delete(note)
    db.session.commit()
    return api_success(message="Notification deleted")
