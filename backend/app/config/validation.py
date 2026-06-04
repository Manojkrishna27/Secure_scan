"""Validate required configuration on application startup."""
import logging
import os

logger = logging.getLogger(__name__)

_INSECURE_VALUES = frozenset(
    {
        "",
        "change_me",
        "dev-secret-change-in-production",
        "password",
        "securescan_pass",
    }
)


def validate_config(app) -> None:
    """Raise on missing or weak secrets in production; warn in development."""
    if app.config.get("TESTING"):
        return

    env = os.getenv("FLASK_ENV", "development")
    secret = app.config.get("SECRET_KEY") or ""
    jwt_secret = app.config.get("JWT_SECRET_KEY") or ""

    if env == "production":
        _require_strong_secret("SECRET_KEY", secret)
        _require_strong_secret("JWT_SECRET_KEY", jwt_secret)
        if not os.getenv("DATABASE_URL") and not os.getenv("MYSQL_PASSWORD"):
            raise RuntimeError(
                "DATABASE_URL or MYSQL_PASSWORD must be set in production."
            )
        mysql_password = os.getenv("MYSQL_PASSWORD", "")
        if not os.getenv("DATABASE_URL") and mysql_password in _INSECURE_VALUES:
            raise RuntimeError(
                "MYSQL_PASSWORD must be set to a non-default value in production."
            )
        logger.info("Production configuration validated.")
        return

    if secret in _INSECURE_VALUES or len(secret) < 16:
        logger.warning(
            "SECRET_KEY is weak or unset. Set a strong SECRET_KEY before deploying."
        )
    if jwt_secret in _INSECURE_VALUES or len(jwt_secret) < 16:
        logger.warning(
            "JWT_SECRET_KEY is weak or unset. Set a strong JWT_SECRET_KEY before deploying."
        )


def _require_strong_secret(name: str, value: str) -> None:
    if value in _INSECURE_VALUES or len(value) < 32:
        raise RuntimeError(
            f"{name} must be set in the environment to a strong random value "
            f"(at least 32 characters) when FLASK_ENV=production."
        )
