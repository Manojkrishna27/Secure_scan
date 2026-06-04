"""Authentication and authorization decorators."""
from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.extensions import db
from app.models import User, UserRole
from app.utils.responses import api_error


def admin_required(fn):
    """Require authenticated user with admin role (JWT + database check)."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user or user.deleted_at is not None or not user.is_active:
            return api_error("Account is not authorized", 403)

        role = user.role.value if isinstance(user.role, UserRole) else user.role
        if role != "admin":
            return api_error("Access denied", 403)
        return fn(*args, **kwargs)

    return wrapper
