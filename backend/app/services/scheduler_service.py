"""APScheduler background jobs for domain monitoring."""
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def _tick_job(app):
    """Run due domain scans inside Flask app context."""
    with app.app_context():
        from app.services.monitoring_service import MonitoringService

        try:
            count = MonitoringService().run_due_domains()
            if count:
                logger.info("Monitoring scheduler processed %s domain(s)", count)
        except Exception as exc:
            logger.exception("Monitoring scheduler error: %s", exc)


def init_scheduler(app):
    """Start APScheduler unless disabled or in tests."""
    global scheduler

    if app.config.get("TESTING"):
        return None
    if os.getenv("DISABLE_SCHEDULER", "").lower() in ("1", "true", "yes"):
        return None
    if scheduler is not None:
        return scheduler

    interval_minutes = int(os.getenv("MONITOR_SCHEDULER_INTERVAL_MINUTES", "15"))

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=lambda: _tick_job(app),
        trigger="interval",
        minutes=interval_minutes,
        id="monitoring_tick",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Monitoring scheduler started (every %s minutes)", interval_minutes
    )
    return scheduler


def shutdown_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown(wait=False)
        scheduler = None
