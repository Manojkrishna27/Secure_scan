"""Admin dashboard, user management, analytics, and audit APIs."""
from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.middleware.auth import admin_required
from app.services.admin_service import (
    export_audit_logs_csv,
    export_scans_csv,
    export_users_csv,
    get_analytics,
    get_audit_logs,
    get_platform_stats,
    get_recent_activity,
    get_system_health,
    get_user,
    global_search,
    list_users,
    soft_delete_user,
    update_user,
)
from app.utils.responses import api_error, api_success

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _admin_id() -> int:
    return int(get_jwt_identity())


@admin_bp.get("/stats")
@jwt_required()
@admin_required
def stats():
    return api_success(data=get_platform_stats())


@admin_bp.get("/analytics")
@jwt_required()
@admin_required
def analytics():
    period = request.args.get("period", "daily")
    return api_success(data=get_analytics(period))


@admin_bp.get("/recent")
@jwt_required()
@admin_required
def recent():
    return api_success(data=get_recent_activity())


@admin_bp.get("/health")
@jwt_required()
@admin_required
def system_health():
    return api_success(data=get_system_health())


@admin_bp.get("/users")
@jwt_required()
@admin_required
def users_list():
    include_deleted = request.args.get("include_deleted", "false").lower() == "true"
    return api_success(data={"users": list_users(include_deleted)})


@admin_bp.get("/users/<int:user_id>")
@jwt_required()
@admin_required
def user_detail(user_id):
    user = get_user(user_id)
    if not user:
        return api_error("User not found", 404)
    return api_success(data={"user": user.to_admin_dict()})


@admin_bp.put("/users/<int:user_id>")
@jwt_required()
@admin_required
def user_update(user_id):
    data = request.get_json(silent=True) or {}
    try:
        user = update_user(_admin_id(), user_id, data)
    except ValueError as exc:
        return api_error(str(exc), 400)
    return api_success(
        data={"user": user.to_admin_dict()},
        message="User updated",
    )


@admin_bp.delete("/users/<int:user_id>")
@jwt_required()
@admin_required
def user_delete(user_id):
    try:
        soft_delete_user(_admin_id(), user_id)
    except ValueError as exc:
        return api_error(str(exc), 400)
    return api_success(message="User deleted")


@admin_bp.get("/audit-logs")
@jwt_required()
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    action = request.args.get("action")
    admin_id = request.args.get("admin_id", type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    return api_success(
        data=get_audit_logs(page, per_page, action, admin_id, date_from, date_to)
    )


@admin_bp.get("/search")
@jwt_required()
@admin_required
def search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return api_error("Search query must be at least 2 characters", 400)
    limit = min(request.args.get("limit", 10, type=int), 50)
    return api_success(data=global_search(q, limit))


@admin_bp.get("/export/users")
@jwt_required()
@admin_required
def export_users():
    return Response(
        export_users_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )


@admin_bp.get("/export/scans")
@jwt_required()
@admin_required
def export_scans():
    return Response(
        export_scans_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scans.csv"},
    )


@admin_bp.get("/export/audit-logs")
@jwt_required()
@admin_required
def export_audit_logs():
    return Response(
        export_audit_logs_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_logs.csv"},
    )


@admin_bp.get("/admin-only")
@jwt_required()
@admin_required
def admin_only():
    return api_success(message="Admin access granted")
