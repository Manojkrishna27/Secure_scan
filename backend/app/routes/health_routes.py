"""Health check endpoints."""
from flask import Blueprint

from app.extensions import db
from app.utils.responses import api_success

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health_check():
    """Liveness + database connectivity (used by Docker healthcheck)."""
    db_status = "connected"
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        db_status = "unavailable"
    status = "healthy" if db_status == "connected" else "degraded"
    return api_success(
        data={
            "status": status,
            "service": "SecureScan AI",
            "database": db_status,
        },
        message="Service is healthy" if status == "healthy" else "Database unavailable",
    )
