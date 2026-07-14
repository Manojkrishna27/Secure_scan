"""Configuration management."""
import os
from datetime import timedelta


def _mysql_uri(
    user: str | None = None,
    password: str | None = None,
    host: str | None = None,
    port: str | None = None,
    database: str | None = None,
) -> str:
    return (
        f"mysql+pymysql://{user or os.getenv('MYSQL_USER', 'securescan')}:"
        f"{password if password is not None else os.getenv('MYSQL_PASSWORD', '')}@"
        f"{host or os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{port or os.getenv('MYSQL_PORT', '3306')}/"
        f"{database or os.getenv('MYSQL_DB', os.getenv('MYSQL_DATABASE', 'securescan'))}"
    )


def _database_uri(*, require_password: bool = False) -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    password = os.getenv("MYSQL_PASSWORD", "")
    if require_password and not password:
        raise RuntimeError(
            "MYSQL_PASSWORD or DATABASE_URL must be set. "
            "Copy backend/.env.example to backend/.env and configure credentials."
        )
    return _mysql_uri(password=password or os.getenv("MYSQL_PASSWORD", "password"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800"))
    )
    JWT_BLOCKLIST_ENABLED = True
    JWT_BLOCKLIST_TOKEN_CHECKS = ["access"]

    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    )

    REPORTS_STORAGE_PATH = os.getenv(
        "REPORTS_STORAGE_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "storage",
            "reports",
        ),
    )

    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_ENABLED = True

    # Gemini AI integration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-not-for-production-use")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-only-not-for-production")
    SQLALCHEMY_DATABASE_URI = _database_uri(require_password=False)


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")


class TestingConfig(Config):
    TESTING = True
    RATELIMIT_ENABLED = False
    DEBUG = True
    SECRET_KEY = "test-secret-key-for-pytest-only-32chars!!"
    JWT_SECRET_KEY = "test-jwt-secret-key-for-pytest-only-32c!"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
