"""Centralized application logging."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app) -> None:
    """Configure app-wide logging (console + optional file)."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    app.logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    if not app.debug and not app.config.get("TESTING"):
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
        )
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "securescan.log"),
            maxBytes=2_000_000,
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

    for name in ("securescan.auth", "securescan.scan", "securescan.report", "securescan.monitoring", "securescan.admin"):
        logging.getLogger(name).setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
