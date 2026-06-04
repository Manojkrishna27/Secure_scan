"""Domain monitoring, change detection, and alerts."""
from datetime import datetime

from app.extensions import db
from app.models import MonitoringDomain, MonitoringHistory, Notification
from app.services.scan_pipeline import run_scan_and_save
from app.utils.app_logging import get_logger
from app.utils.url_validator import normalize_and_validate_url

monitor_log = get_logger("securescan.monitoring")

HEADER_LABELS = {
    "hsts": "Strict-Transport-Security",
    "csp": "Content-Security-Policy",
    "x_frame_options": "X-Frame-Options",
    "x_content_type_options": "X-Content-Type-Options",
    "referrer_policy": "Referrer-Policy",
    "permissions_policy": "Permissions-Policy",
}


def normalize_domain_input(domain: str) -> str:
    """Normalize user input to hostname (e.g. github.com)."""
    raw = domain.strip()
    if not raw.startswith("http"):
        raw = f"https://{raw}"
    _, hostname, normalized_domain = normalize_and_validate_url(raw)
    return normalized_domain or hostname


class MonitoringService:
    """Run monitored domain scans and generate notifications."""

    def add_domain(self, user_id: int, domain: str, frequency: str) -> MonitoringDomain:
        frequency = frequency.lower()
        if frequency not in ("daily", "weekly"):
            raise ValueError("monitoring_frequency must be 'daily' or 'weekly'.")

        hostname = normalize_domain_input(domain)
        existing = MonitoringDomain.query.filter_by(
            user_id=user_id, domain=hostname
        ).first()
        if existing:
            raise ValueError(f"Domain {hostname} is already being monitored.")

        now = datetime.utcnow()
        record = MonitoringDomain(
            user_id=user_id,
            domain=hostname,
            monitoring_frequency=frequency,
            is_active=True,
            next_scan_at=now,
        )
        record.next_scan_at = record.compute_next_scan_at(now)
        db.session.add(record)
        db.session.commit()
        return record

    def run_domain_scan(self, domain_id: int, user_id: int) -> dict:
        """Execute scan for a monitored domain and return summary."""
        record = MonitoringDomain.query.filter_by(
            id=domain_id, user_id=user_id
        ).first()
        if not record:
            raise ValueError("Monitored domain not found.")
        if not record.is_active:
            raise ValueError("Monitoring is paused for this domain.")

        return self._execute_scan(record)

    def run_due_domains(self) -> int:
        """Scan all domains where next_scan_at <= now. Returns count processed."""
        now = datetime.utcnow()
        due = MonitoringDomain.query.filter(
            MonitoringDomain.is_active.is_(True),
            MonitoringDomain.next_scan_at <= now,
        ).all()
        count = 0
        for record in due:
            try:
                self._execute_scan(record)
                count += 1
            except Exception:
                record.next_scan_at = record.compute_next_scan_at(now)
                db.session.commit()
        return count

    def _execute_scan(self, record: MonitoringDomain) -> dict:
        url = f"https://{record.domain}"
        previous = {
            "score": record.current_score,
            "days_remaining": record.last_days_remaining,
            "tls_versions": record.last_tls_versions or {},
            "security_headers": record.last_security_headers or {},
        }

        scan, payload = run_scan_and_save(record.user_id, url, commit=False)

        notifications_created = self._compare_and_notify(
            record, previous, payload
        )

        now = datetime.utcnow()
        history = MonitoringHistory(
            monitoring_domain_id=record.id,
            score=payload.get("security_score"),
            risk_level=payload.get("risk_level"),
            scan_date=now,
            scan_id=scan.id,
        )
        db.session.add(history)

        record.current_score = payload.get("security_score")
        record.current_risk_level = payload.get("risk_level")
        record.last_scan_at = now
        record.last_days_remaining = payload.get("days_remaining")
        record.last_tls_versions = payload.get("tls_versions")
        record.last_security_headers = payload.get("security_headers")
        record.last_scan_id = scan.id
        record.next_scan_at = record.compute_next_scan_at(now)

        db.session.commit()

        return {
            "domain": record.to_dict(),
            "scan_id": scan.id,
            "notifications_created": notifications_created,
        }

    def _compare_and_notify(
        self,
        record: MonitoringDomain,
        previous: dict,
        new_payload: dict,
    ) -> int:
        """Compare scans and create notifications. Returns count created."""
        count = 0
        domain = record.domain
        user_id = record.user_id

        days = new_payload.get("days_remaining")
        prev_days = previous.get("days_remaining")
        if days is not None:
            if days <= 7 and (prev_days is None or prev_days > 7):
                count += self._notify(
                    user_id,
                    domain,
                    "SSL certificate expiring soon",
                    f"SSL certificate for {domain} expires in {days} days.",
                    "High",
                )
            elif days <= 30 and (prev_days is None or prev_days > 30):
                count += self._notify(
                    user_id,
                    domain,
                    "SSL certificate renewal reminder",
                    f"SSL certificate for {domain} expires in {days} days.",
                    "Medium",
                )

        old_score = previous.get("score")
        new_score = new_payload.get("security_score")
        if old_score is not None and new_score is not None:
            drop = old_score - new_score
            if drop >= 10:
                count += self._notify(
                    user_id,
                    domain,
                    "Security score dropped",
                    f"Security score dropped from {old_score} to {new_score}.",
                    "High",
                )

        old_tls = previous.get("tls_versions") or {}
        new_tls = new_payload.get("tls_versions") or {}
        if old_tls.get("tls_1_3") and not new_tls.get("tls_1_3"):
            count += self._notify(
                user_id,
                domain,
                "TLS downgrade detected",
                f"TLS 1.3 support removed on {domain}.",
                "High",
            )
        if (old_tls.get("tls_1_2") or old_tls.get("tls_1_3")) and not (
            new_tls.get("tls_1_2") or new_tls.get("tls_1_3")
        ):
            count += self._notify(
                user_id,
                domain,
                "TLS downgrade detected",
                f"Modern TLS support reduced on {domain}.",
                "High",
            )

        old_headers = previous.get("security_headers") or {}
        new_headers = new_payload.get("security_headers") or {}
        for key, label in HEADER_LABELS.items():
            if old_headers.get(key) and not new_headers.get(key):
                count += self._notify(
                    user_id,
                    domain,
                    "Security header removed",
                    f"{label} header removed on {domain}.",
                    "Medium",
                )

        return count

    def _notify(
        self,
        user_id: int,
        domain: str,
        title: str,
        message: str,
        severity: str,
    ) -> int:
        note = Notification(
            user_id=user_id,
            domain=domain,
            title=title,
            message=message,
            severity=severity,
            is_read=False,
        )
        db.session.add(note)
        return 1

    def get_summary(self, user_id: int) -> dict:
        domains = MonitoringDomain.query.filter_by(user_id=user_id).all()
        ssl_expiring = sum(
            1
            for d in domains
            if d.last_days_remaining is not None and d.last_days_remaining <= 30
        )
        high_risk = sum(
            1
            for d in domains
            if d.current_risk_level
            and "high" in d.current_risk_level.lower()
        )
        return {
            "total_monitored": len(domains),
            "active_monitored": sum(1 for d in domains if d.is_active),
            "ssl_expiring_soon": ssl_expiring,
            "high_risk_domains": high_risk,
        }

    def get_trend_data(self, user_id: int, limit: int = 20) -> list:
        """Aggregate monitoring history for dashboard chart."""
        domains = MonitoringDomain.query.filter_by(user_id=user_id).all()
        if not domains:
            return []
        domain_ids = [d.id for d in domains]
        rows = (
            MonitoringHistory.query.filter(
                MonitoringHistory.monitoring_domain_id.in_(domain_ids)
            )
            .order_by(MonitoringHistory.scan_date.asc())
            .limit(limit * len(domain_ids))
            .all()
        )
        return [r.to_dict() for r in rows[-limit:]]
