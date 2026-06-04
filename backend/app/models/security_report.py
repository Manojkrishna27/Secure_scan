"""Security report (PDF) model."""
from datetime import datetime

from app.extensions import db


class SecurityReport(db.Model):
    __tablename__ = "security_reports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scan_id = db.Column(
        db.BigInteger,
        db.ForeignKey("scan_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    report_name = db.Column(db.String(255), nullable=False)
    report_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="security_reports")
    scan = db.relationship("ScanResult", back_populates="security_reports")

    def to_dict(self, *, include_path: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "scan_id": self.scan_id,
            "report_name": self.report_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scan_url": self.scan.url if self.scan else None,
            "domain": self.scan.domain if self.scan else None,
            "security_score": self.scan.security_score if self.scan else None,
        }
        if include_path:
            data["report_path"] = self.report_path
        return data
