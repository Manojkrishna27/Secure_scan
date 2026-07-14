#!/usr/bin/env python3
"""
Seed realistic demo data: 2 users, 8 scans, 3 monitored domains, 4 notifications.
Run from project root:
    cd backend && python ../scripts/seed_data.py
"""
import os
import sys
from datetime import datetime, timedelta
import json
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app import create_app
from app.extensions import db
from app.models import (
    MonitoringDomain,
    Notification,
    ScanResult,
    User,
    UserRole,
)

# ── Seed data ─────────────────────────────────────────────────────────────────

USERS = [
    {
        "full_name": "System Admin",
        "email": "admin@securescan.ai",
        "password": "Admin12345",
        "role": UserRole.admin,
    },
    {
        "full_name": "Demo User",
        "email": "demo@securescan.ai",
        "password": "Demo12345",
        "role": UserRole.user,
    },
]

SCANS = [
    {
        "url": "https://github.com",
        "domain": "github.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 95,
        "risk_level": "Low Risk",
        "grade": "A+",
        "issuer": "DigiCert Inc",
        "common_name": "github.com",
        "organization": "GitHub, Inc.",
        "days_remaining": 312,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": True, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": False,
        },
        "findings": [],
        "ai_summary": "GitHub demonstrates excellent security posture. All critical headers are present, TLS 1.3 is enabled, and the SSL certificate is valid for over 10 months.",
        "days_ago": 0,
    },
    {
        "url": "https://google.com",
        "domain": "google.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 92,
        "risk_level": "Low Risk",
        "grade": "A",
        "issuer": "Google Trust Services LLC",
        "common_name": "google.com",
        "organization": "Google LLC",
        "days_remaining": 87,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": True, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": True,
        },
        "findings": [],
        "ai_summary": "Google.com shows a strong security configuration. All major security headers are properly implemented.",
        "days_ago": 1,
    },
    {
        "url": "https://cloudflare.com",
        "domain": "cloudflare.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 98,
        "risk_level": "Low Risk",
        "grade": "A+",
        "issuer": "DigiCert SHA2 Secure Server CA",
        "common_name": "cloudflare.com",
        "organization": "Cloudflare, Inc.",
        "days_remaining": 224,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": True, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": True,
        },
        "findings": [],
        "ai_summary": "Cloudflare exemplifies best-in-class security configuration. All security controls are properly implemented.",
        "days_ago": 2,
    },
    {
        "url": "https://stackoverflow.com",
        "domain": "stackoverflow.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.2",
        "security_score": 78,
        "risk_level": "Medium Risk",
        "grade": "B+",
        "issuer": "Let's Encrypt",
        "common_name": "stackoverflow.com",
        "organization": None,
        "days_remaining": 45,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": False},
        "security_headers": {
            "hsts": True, "csp": False, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": False,
        },
        "findings": [
            {"severity": "Medium", "title": "TLS 1.3 Not Supported", "recommendation": "Enable TLS 1.3 to improve security and performance."},
            {"severity": "Medium", "title": "Missing Content-Security-Policy", "recommendation": "Implement a strict CSP header to mitigate XSS attacks."},
            {"severity": "Low", "title": "SSL Certificate Expiring Soon", "recommendation": "Certificate expires in 45 days. Renew before expiry to avoid service disruption."},
        ],
        "ai_summary": "Stack Overflow has adequate but improvable security. TLS 1.3 is not enabled and the CSP header is missing.",
        "days_ago": 3,
    },
    {
        "url": "https://reddit.com",
        "domain": "reddit.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 82,
        "risk_level": "Medium Risk",
        "grade": "B+",
        "issuer": "Amazon",
        "common_name": "reddit.com",
        "organization": "Reddit, Inc.",
        "days_remaining": 156,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": False, "x_frame_options": False,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": False,
        },
        "findings": [
            {"severity": "Medium", "title": "Missing Content-Security-Policy", "recommendation": "Implement a strict CSP header to mitigate XSS attacks."},
            {"severity": "Medium", "title": "Missing X-Frame-Options", "recommendation": "Add X-Frame-Options: DENY to prevent clickjacking attacks."},
        ],
        "ai_summary": "Reddit has good TLS configuration but is missing key security headers — CSP and X-Frame-Options are absent.",
        "days_ago": 5,
    },
    {
        "url": "https://example-oldsite.com",
        "domain": "example-oldsite.com",
        "ssl_status": "expired",
        "tls_version": "TLSv1.0",
        "security_score": 22,
        "risk_level": "High Risk",
        "grade": "F",
        "issuer": "Unknown CA",
        "common_name": "example-oldsite.com",
        "organization": None,
        "days_remaining": -15,
        "tls_versions": {"tls_1_0": True, "tls_1_1": True, "tls_1_2": False, "tls_1_3": False},
        "security_headers": {
            "hsts": False, "csp": False, "x_frame_options": False,
            "x_content_type_options": False, "referrer_policy": False, "permissions_policy": False,
        },
        "findings": [
            {"severity": "Critical", "title": "SSL Certificate Expired", "recommendation": "Renew SSL certificate immediately. Site is currently untrusted."},
            {"severity": "High", "title": "TLS 1.0 and 1.1 Enabled", "recommendation": "Disable deprecated TLS 1.0 and 1.1. Only support TLS 1.2+."},
            {"severity": "High", "title": "No Security Headers", "recommendation": "Implement all critical security headers immediately."},
            {"severity": "High", "title": "Missing HSTS", "recommendation": "Enable HTTP Strict Transport Security to prevent downgrade attacks."},
        ],
        "ai_summary": "CRITICAL: This site has severe security vulnerabilities. SSL certificate is expired and only deprecated TLS protocols are supported.",
        "days_ago": 7,
    },
    {
        "url": "https://wikipedia.org",
        "domain": "wikipedia.org",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 88,
        "risk_level": "Medium Risk",
        "grade": "A-",
        "issuer": "DigiCert Inc",
        "common_name": "wikipedia.org",
        "organization": "Wikimedia Foundation, Inc.",
        "days_remaining": 198,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": True, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": False, "permissions_policy": False,
        },
        "findings": [
            {"severity": "Low", "title": "Missing Referrer-Policy", "recommendation": "Add Referrer-Policy header to control referrer information."},
            {"severity": "Low", "title": "Missing Permissions-Policy", "recommendation": "Implement Permissions-Policy to control browser feature access."},
        ],
        "ai_summary": "Wikipedia has a solid security foundation. Only minor header improvements are needed.",
        "days_ago": 10,
    },
    {
        "url": "https://github.com",
        "domain": "github.com",
        "ssl_status": "valid",
        "tls_version": "TLSv1.3",
        "security_score": 94,
        "risk_level": "Low Risk",
        "grade": "A+",
        "issuer": "DigiCert Inc",
        "common_name": "github.com",
        "organization": "GitHub, Inc.",
        "days_remaining": 321,
        "tls_versions": {"tls_1_0": False, "tls_1_1": False, "tls_1_2": True, "tls_1_3": True},
        "security_headers": {
            "hsts": True, "csp": True, "x_frame_options": True,
            "x_content_type_options": True, "referrer_policy": True, "permissions_policy": False,
        },
        "findings": [],
        "ai_summary": "GitHub maintains excellent security posture.",
        "days_ago": 14,
    },
]

DOMAINS = [
    {"domain": "github.com", "frequency": "daily", "score": 95, "risk": "Low Risk"},
    {"domain": "stackoverflow.com", "frequency": "weekly", "score": 78, "risk": "Medium Risk"},
    {"domain": "example-oldsite.com", "frequency": "daily", "score": 22, "risk": "High Risk"},
]


# ── Runner ─────────────────────────────────────────────────────────────────────

def main():
    app = create_app()
    with app.app_context():
        # ── Users ──
        user_objs = {}
        for ud in USERS:
            existing = User.query.filter_by(email=ud["email"]).first()
            if not existing:
                u = User(full_name=ud["full_name"], email=ud["email"], role=ud["role"], is_active=True)
                u.set_password(ud["password"])
                db.session.add(u)
                db.session.flush()
                print(f"  Created user: {ud['email']}")
                user_objs[ud["email"]] = u
            else:
                existing.role = ud["role"]
                existing.set_password(ud["password"])
                existing.is_active = True
                print(f"  Updated user: {ud['email']}")
                user_objs[ud["email"]] = existing
        db.session.commit()

        demo_user = user_objs.get("demo@securescan.ai") or User.query.filter_by(email="demo@securescan.ai").first()
        admin_user = user_objs.get("admin@securescan.ai") or User.query.filter_by(email="admin@securescan.ai").first()

        # ── Scans ──
        now = datetime.utcnow()
        scan_objs = []
        for sd in SCANS:
            existing = ScanResult.query.filter_by(url=sd["url"], domain=sd["domain"]).order_by(
                ScanResult.scan_date.desc()
            ).first()
            if existing and abs((existing.scan_date - (now - timedelta(days=sd["days_ago"]))).total_seconds()) < 86400:
                scan_objs.append(existing)
                print(f"  Scan already exists for {sd['url']}, skipping.")
                continue

            scan = ScanResult(
                user_id=demo_user.id,
                url=sd["url"],
                domain=sd["domain"],
                ssl_status=sd["ssl_status"],
                tls_version=sd["tls_version"],
                security_score=sd["security_score"],
                risk_level=sd["risk_level"],
                grade=sd["grade"],
                issuer=sd.get("issuer"),
                common_name=sd.get("common_name"),
                organization=sd.get("organization"),
                days_remaining=sd.get("days_remaining"),
                tls_versions=sd.get("tls_versions", {}),
                security_headers=sd.get("security_headers", {}),
                findings=sd.get("findings", []),
                ai_summary=sd.get("ai_summary"),
                scan_date=now - timedelta(days=sd["days_ago"]),
            )
            db.session.add(scan)
            db.session.flush()
            scan_objs.append(scan)
            print(f"  Created scan: {sd['url']} (score={sd['security_score']})")
        db.session.commit()

        # ── Monitored Domains ──
        for dd in DOMAINS:
            existing = MonitoringDomain.query.filter_by(user_id=demo_user.id, domain=dd["domain"]).first()
            if existing:
                print(f"  Monitoring domain already exists: {dd['domain']}, skipping.")
                continue
            md = MonitoringDomain(
                user_id=demo_user.id,
                domain=dd["domain"],
                monitoring_frequency=dd["frequency"],
                is_active=True,
                current_score=dd["score"],
                current_risk_level=dd["risk"],
                last_scan_at=now - timedelta(hours=random.randint(1, 48)),
            )
            db.session.add(md)
            print(f"  Created monitored domain: {dd['domain']}")
        db.session.commit()

        # ── Notifications ──
        notifs = [
            {
                "user_id": demo_user.id,
                "domain": "example-oldsite.com",
                "title": "🔴 SSL Certificate Expired",
                "message": "SSL certificate for example-oldsite.com expired 15 days ago. Immediate renewal required.",
                "severity": "critical",
            },
            {
                "user_id": demo_user.id,
                "domain": "stackoverflow.com",
                "title": "⚠️ SSL Certificate Expiring Soon",
                "message": "SSL certificate for stackoverflow.com expires in 45 days. Schedule renewal now.",
                "severity": "warning",
            },
            {
                "user_id": demo_user.id,
                "domain": "example-oldsite.com",
                "title": "🔴 High Risk Domain Detected",
                "message": "example-oldsite.com scored 22/100 — critical security vulnerabilities detected.",
                "severity": "high",
            },
            {
                "user_id": demo_user.id,
                "domain": "github.com",
                "title": "✅ Security Score Improved",
                "message": "github.com security score improved to 95/100. Excellent posture maintained.",
                "severity": "info",
            },
        ]
        existing_count = Notification.query.filter_by(user_id=demo_user.id).count()
        if existing_count == 0:
            for nd in notifs:
                n = Notification(
                    user_id=nd["user_id"],
                    domain=nd["domain"],
                    title=nd["title"],
                    message=nd["message"],
                    severity=nd["severity"],
                )
                db.session.add(n)
                print(f"  Created notification: {nd['title']}")
            db.session.commit()
        else:
            print(f"  Notifications already exist ({existing_count}), skipping.")

        print("\n✅ Seed data created successfully!")
        print(f"   Admin: admin@securescan.ai / Admin12345")
        print(f"   Demo:  demo@securescan.ai  / Demo12345")


if __name__ == "__main__":
    main()
