"""Admin audit log model."""
from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = db.Column(db.String(64), nullable=False, index=True)
    target_type = db.Column(db.String(64), nullable=False)
    target_id = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    admin = db.relationship("User", foreign_keys=[admin_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "admin_name": self.admin.full_name if self.admin else None,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
