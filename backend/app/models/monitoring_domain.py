"""Monitored domain model."""
from datetime import datetime, timedelta

from app.extensions import db


class MonitoringDomain(db.Model):
    __tablename__ = "monitoring_domains"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain = db.Column(db.String(255), nullable=False, index=True)
    monitoring_frequency = db.Column(
        db.String(16), nullable=False, default="daily"
    )  # daily | weekly
    last_scan_at = db.Column(db.DateTime, nullable=True)
    next_scan_at = db.Column(db.DateTime, nullable=True, index=True)
    current_score = db.Column(db.Integer, nullable=True)
    current_risk_level = db.Column(db.String(32), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Baseline for change detection (updated after each scan)
    last_days_remaining = db.Column(db.Integer, nullable=True)
    last_tls_versions = db.Column(db.JSON, nullable=True)
    last_security_headers = db.Column(db.JSON, nullable=True)
    last_scan_id = db.Column(db.BigInteger, db.ForeignKey("scan_results.id"), nullable=True)

    user = db.relationship("User", back_populates="monitoring_domains")
    history = db.relationship(
        "MonitoringHistory",
        back_populates="monitoring_domain",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    last_scan = db.relationship("ScanResult", foreign_keys=[last_scan_id])

    def compute_next_scan_at(self, from_time: datetime | None = None) -> datetime:
        base = from_time or datetime.utcnow()
        if self.monitoring_frequency == "weekly":
            return base + timedelta(days=7)
        return base + timedelta(days=1)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "monitoring_frequency": self.monitoring_frequency,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "next_scan_at": self.next_scan_at.isoformat() if self.next_scan_at else None,
            "current_score": self.current_score,
            "current_risk_level": self.current_risk_level,
            "is_active": self.is_active,
            "last_days_remaining": self.last_days_remaining,
            "last_scan_id": self.last_scan_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
