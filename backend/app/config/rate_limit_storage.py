"""Resolve Flask-Limiter storage; fall back when Redis is unreachable."""
import logging

logger = logging.getLogger("securescan.config")


def configure_rate_limit_storage(application) -> None:
    """Use Redis for rate limits when available; otherwise in-memory storage."""
    uri = application.config.get("RATELIMIT_STORAGE_URI") or "memory://"
    if not str(uri).startswith("redis"):
        return
    try:
        import redis

        redis.from_url(uri).ping()
    except Exception as exc:
        logger.warning(
            "Redis unavailable for rate limiting (%s); using memory:// storage.",
            exc,
        )
        application.config["RATELIMIT_STORAGE_URI"] = "memory://"
