"""Flask application factory."""
import os

from flask import Flask
from flask_cors import CORS

from app.config import config_by_name
from app.extensions import bcrypt, db, jwt, limiter, migrate


def create_app(config_name=None):
    """Create and configure the Flask application."""
    application = Flask(__name__)

    env = config_name or os.getenv("FLASK_ENV", "development")
    application.config.from_object(
        config_by_name.get(env, config_by_name["development"])
    )

    if env == "production":
        from app.config import _database_uri

        application.config["SQLALCHEMY_DATABASE_URI"] = _database_uri(
            require_password=True
        )

    db.init_app(application)
    migrate.init_app(application, db)
    jwt.init_app(application)
    bcrypt.init_app(application)
    from app.config.rate_limit_storage import configure_rate_limit_storage

    configure_rate_limit_storage(application)
    limiter.init_app(application)

    origins = application.config.get("CORS_ORIGINS", "")
    if isinstance(origins, str):
        origin_list = [o.strip() for o in origins.split(",") if o.strip()]
    else:
        origin_list = origins
    CORS(application, resources={r"/api/*": {"origins": origin_list}})

    with application.app_context():
        import app.models  # noqa: F401

    _register_jwt_callbacks(jwt)

    from app.routes import register_blueprints
    from app.utils.errors import register_error_handlers

    from app.config.validation import validate_config

    validate_config(application)

    register_blueprints(application)
    register_error_handlers(application)
    _register_security_headers(application)

    from app.utils.app_logging import setup_logging

    setup_logging(application)

    from app.services.scheduler_service import init_scheduler

    init_scheduler(application)

    return application


def _register_security_headers(application):
    @application.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'",
        )
        return response


def _register_jwt_callbacks(jwt_manager):
    from app.models import TokenBlocklist, User

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return TokenBlocklist.query.filter_by(jti=jti).first() is not None

    @jwt_manager.token_verification_loader
    def verify_active_user(jwt_header, jwt_payload):
        user = db.session.get(User, int(jwt_payload["sub"]))
        if not user or not user.is_active or user.deleted_at is not None:
            return False
        return True
