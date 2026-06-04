"""Monitoring scan history for trend charts."""
from datetime import datetime

from app.extensions import db


class MonitoringHistory(db.Model):
    __tablename__ = "monitoring_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    monitoring_domain_id = db.Column(
        db.Integer,
        db.ForeignKey("monitoring_domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(32), nullable=True)
    scan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    scan_id = db.Column(db.BigInteger, db.ForeignKey("scan_results.id"), nullable=True)

    monitoring_domain = db.relationship("MonitoringDomain", back_populates="history")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "monitoring_domain_id": self.monitoring_domain_id,
            "score": self.score,
            "risk_level": self.risk_level,
            "scan_date": self.scan_date.isoformat() if self.scan_date else None,
            "scan_id": self.scan_id,
        }
