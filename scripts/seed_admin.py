#!/usr/bin/env python3
"""Create default admin user for testing."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from app import create_app
from app.extensions import db
from app.models import User, UserRole


def main():
    app = create_app()
    email = os.getenv("ADMIN_EMAIL", "admin@securescan.ai")
    password = os.getenv("ADMIN_PASSWORD", "Admin12345")
    full_name = os.getenv("ADMIN_FULL_NAME", "System Admin")

    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            existing.role = UserRole.admin
            existing.set_password(password)
            existing.is_active = True
            db.session.commit()
            print(f"Updated admin user: {email}")
            return

        user = User(
            full_name=full_name,
            email=email,
            role=UserRole.admin,
            is_active=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Created admin user: {email}")


if __name__ == "__main__":
    main()
