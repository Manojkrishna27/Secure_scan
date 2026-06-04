"""API error handlers."""
from flask import jsonify
from flask_limiter.errors import RateLimitExceeded
from flask_jwt_extended.exceptions import (
    FreshTokenRequired,
    InvalidHeaderError,
    JWTDecodeError,
    NoAuthorizationError,
    RevokedTokenError,
)
from jwt.exceptions import ExpiredSignatureError
from werkzeug.exceptions import BadRequest, HTTPException

from app.utils.responses import api_error


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        msg = getattr(e, "description", "Bad request")
        return api_error(msg, 400)

    @app.errorhandler(404)
    def not_found(e):
        return api_error("Resource not found", 404)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Unhandled error: %s", e)
        return api_error("Internal server error", 500)

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if e.code == 500:
            app.logger.exception("HTTP 500: %s", e)
            return api_error("Internal server error", 500)
        return api_error(e.description or "Request failed", e.code or 400)

    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return api_error(e.description, 400)

    @app.errorhandler(NoAuthorizationError)
    def handle_missing_jwt(e):
        return api_error("Authorization token required", 401)

    @app.errorhandler(JWTDecodeError)
    @app.errorhandler(InvalidHeaderError)
    @app.errorhandler(ExpiredSignatureError)
    def handle_invalid_jwt(e):
        return api_error("Invalid or expired token", 401)

    @app.errorhandler(RevokedTokenError)
    def handle_revoked_jwt(e):
        return api_error("Token has been revoked", 401)

    @app.errorhandler(FreshTokenRequired)
    def handle_fresh_token(e):
        return api_error("Fresh token required", 401)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return api_error("Too many requests. Please try again later.", 429)
