"""Authentication routes."""
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db, limiter
from app.models import TokenBlocklist, User
from app.utils.app_logging import get_logger
from app.utils.responses import api_error, api_success
from app.utils.validators import (
    validate_email,
    validate_full_name,
    validate_password,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_log = get_logger("securescan.auth")


def _get_current_user():
    user_id = get_jwt_identity()
    return db.session.get(User, int(user_id))


@auth_bp.post("/register")
@limiter.limit("10 per hour")
def register():
    data = request.get_json(silent=True) or {}

    ok, full_name = validate_full_name(data.get("full_name"))
    if not ok:
        return api_error(full_name, 400)

    ok, email = validate_email(data.get("email"))
    if not ok:
        return api_error(email, 400)

    password = data.get("password", "")
    ok, msg = validate_password(password)
    if not ok:
        return api_error(msg, 400)

    if User.query.filter_by(email=email).filter(User.deleted_at.is_(None)).first():
        return api_error("Email already registered", 409)

    user = User(full_name=full_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    auth_log.info("User registered: %s", email)

    return api_success(message="User registered successfully", status=201)


@auth_bp.post("/login")
@limiter.limit("20 per hour")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return api_error("Email and password are required", 400)

    user = User.query.filter_by(email=email).first()
    if not user or user.deleted_at is not None or not user.check_password(password):
        auth_log.warning("Failed login attempt for email=%s", email)
        return api_error("Invalid email or password", 401)

    if not user.is_active:
        auth_log.warning("Login blocked (inactive) for email=%s", email)
        return api_error("Account is deactivated", 403)

    role = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": role},
    )
    auth_log.info("Successful login for user_id=%s", user.id)

    return api_success(
        data={"access_token": access_token, "user": user.to_dict()},
        message="Login successful",
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    user = _get_current_user()
    if not user:
        return api_error("User not found", 404)
    if not user.is_active or user.deleted_at is not None:
        return api_error("Account is deactivated", 403)
    return api_success(data={"user": user.to_dict()})


@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    user = _get_current_user()
    if not user:
        return api_error("User not found", 404)

    data = request.get_json(silent=True) or {}
    ok, full_name = validate_full_name(data.get("full_name"))
    if not ok:
        return api_error(full_name, 400)

    user.full_name = full_name
    db.session.commit()

    return api_success(
        data={"user": user.to_dict()},
        message="Profile updated successfully",
    )


@auth_bp.put("/change-password")
@jwt_required()
def change_password():
    user = _get_current_user()
    if not user:
        return api_error("User not found", 404)

    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return api_error("Current and new password are required", 400)

    if not user.check_password(current_password):
        return api_error("Current password is incorrect", 400)

    ok, msg = validate_password(new_password)
    if not ok:
        return api_error(msg, 400)

    user.set_password(new_password)
    db.session.commit()

    return api_success(message="Password changed successfully")


@auth_bp.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    if not TokenBlocklist.query.filter_by(jti=jti).first():
        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
    return api_success(message="Logged out successfully")
