"""User model."""
import enum
from datetime import datetime

from app.extensions import bcrypt, db


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum(UserRole),
        default=UserRole.user,
        nullable=False,
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    scan_results = db.relationship(
        "ScanResult",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    security_reports = db.relationship(
        "SecurityReport",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    monitoring_domains = db.relationship(
        "MonitoringDomain",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def to_dict(self) -> dict:
        role = self.role.value if isinstance(self.role, UserRole) else self.role
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": role,
            "is_active": self.is_active,
        }

    def to_admin_dict(self) -> dict:
        data = self.to_dict()
        data.update(
            {
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
                "status": "deleted" if self.is_deleted else ("active" if self.is_active else "suspended"),
            }
        )
        return data
