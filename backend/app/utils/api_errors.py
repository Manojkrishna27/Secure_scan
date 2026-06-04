"""Safe API error responses — log internally, return generic messages to clients."""
import logging

logger = logging.getLogger(__name__)


def log_and_message(
    exc: BaseException,
    *,
    user_message: str = "An unexpected error occurred. Please try again.",
    log_message: str | None = None,
) -> str:
    """Log the full exception and return a safe user-facing message."""
    logger.exception(log_message or "Request failed: %s", exc)
    return user_message
