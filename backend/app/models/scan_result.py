"""Scan result model."""
from datetime import datetime

from app.extensions import db


class ScanResult(db.Model):
    __tablename__ = "scan_results"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url = db.Column(db.String(2048), nullable=False)
    domain = db.Column(db.String(255), nullable=False, index=True)
    ssl_status = db.Column(db.String(32), nullable=True)
    issuer = db.Column(db.String(512), nullable=True)
    common_name = db.Column(db.String(255), nullable=True)
    valid_from = db.Column(db.DateTime, nullable=True)
    valid_to = db.Column(db.DateTime, nullable=True)
    days_remaining = db.Column(db.Integer, nullable=True)
    tls_version = db.Column(db.String(32), nullable=True)
    security_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(32), nullable=True)
    grade = db.Column(db.String(8), nullable=True)
    scan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Extended JSON payloads
    organization = db.Column(db.String(512), nullable=True)
    serial_number = db.Column(db.String(128), nullable=True)
    signature_algorithm = db.Column(db.String(128), nullable=True)
    certificate_version = db.Column(db.String(32), nullable=True)
    public_key_algorithm = db.Column(db.String(64), nullable=True)
    domain_name = db.Column(db.String(255), nullable=True)
    tls_versions = db.Column(db.JSON, nullable=True)
    certificate_chain = db.Column(db.JSON, nullable=True)
    security_headers = db.Column(db.JSON, nullable=True)
    header_values = db.Column(db.JSON, nullable=True)
    findings = db.Column(db.JSON, nullable=True)

    ai_summary = db.Column(db.Text, nullable=True)
    ai_risk_assessment = db.Column(db.JSON, nullable=True)
    ai_recommendations = db.Column(db.JSON, nullable=True)

    user = db.relationship("User", back_populates="scan_results")
    security_reports = db.relationship(
        "SecurityReport",
        back_populates="scan",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @staticmethod
    def _parse_dt(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(
                    tzinfo=None
                )
            except ValueError:
                return None
        return None

    @classmethod
    def from_scan_payload(cls, user_id: int, payload: dict) -> "ScanResult":
        return cls(
            user_id=user_id,
            url=payload["url"],
            domain=payload["domain"],
            ssl_status=payload.get("ssl_status"),
            issuer=payload.get("issuer"),
            common_name=payload.get("common_name"),
            domain_name=payload.get("domain_name"),
            organization=payload.get("organization"),
            serial_number=str(payload.get("serial_number") or ""),
            signature_algorithm=payload.get("signature_algorithm"),
            certificate_version=payload.get("certificate_version"),
            public_key_algorithm=payload.get("public_key_algorithm"),
            valid_from=cls._parse_dt(payload.get("valid_from")),
            valid_to=cls._parse_dt(payload.get("valid_to")),
            days_remaining=payload.get("days_remaining"),
            tls_version=payload.get("tls_version"),
            tls_versions=payload.get("tls_versions"),
            certificate_chain=payload.get("certificate_chain"),
            security_headers=payload.get("security_headers"),
            header_values=payload.get("header_values"),
            security_score=payload.get("security_score"),
            risk_level=payload.get("risk_level"),
            grade=payload.get("grade"),
            findings=payload.get("findings"),
            ai_summary=payload.get("ai_summary"),
            ai_risk_assessment=payload.get("ai_risk_assessment"),
            ai_recommendations=payload.get("ai_recommendations"),
            scan_date=cls._parse_dt(payload.get("scan_date")) or datetime.utcnow(),
        )

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "domain": self.domain,
            "security_score": self.security_score,
            "risk_level": self.risk_level,
            "grade": self.grade,
            "scan_date": self.scan_date.isoformat() if self.scan_date else None,
            "ssl_status": self.ssl_status,
        }

    def to_detail(self) -> dict:
        return {
            **self.to_summary(),
            "user_id": self.user_id,
            "ssl_status": self.ssl_status,
            "issuer": self.issuer,
            "common_name": self.common_name,
            "domain_name": self.domain_name,
            "organization": self.organization,
            "serial_number": self.serial_number,
            "signature_algorithm": self.signature_algorithm,
            "certificate_version": self.certificate_version,
            "public_key_algorithm": self.public_key_algorithm,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "days_remaining": self.days_remaining,
            "tls_version": self.tls_version,
            "tls_versions": self.tls_versions or {},
            "certificate_chain": self.certificate_chain or {},
            "security_headers": self.security_headers or {},
            "header_values": self.header_values or {},
            "findings": self.findings or [],
            "ai_summary": self.ai_summary,
            "ai_risk_assessment": self.ai_risk_assessment or {},
            "ai_recommendations": self.ai_recommendations or [],
            "reports": [
                {
                    "id": r.id,
                    "report_name": r.report_name,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in sorted(
                    self.security_reports,
                    key=lambda r: r.created_at or datetime.min,
                    reverse=True,
                )
            ],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def apply_ai_audit(self, ai_payload: dict) -> None:
        self.ai_summary = ai_payload.get("security_summary")
        self.ai_risk_assessment = ai_payload.get("risk_assessment")
        self.ai_recommendations = ai_payload.get("recommendations")
