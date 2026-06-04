"""Phase 4 — monitoring domains, notifications, history.

Revision ID: 005_phase4
Revises: 004_phase3
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_phase4"
down_revision: Union[str, None] = "004_phase3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "monitoring_domains",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("monitoring_frequency", sa.String(length=16), nullable=False),
        sa.Column("last_scan_at", sa.DateTime(), nullable=True),
        sa.Column("next_scan_at", sa.DateTime(), nullable=True),
        sa.Column("current_score", sa.Integer(), nullable=True),
        sa.Column("current_risk_level", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_days_remaining", sa.Integer(), nullable=True),
        sa.Column("last_tls_versions", sa.JSON(), nullable=True),
        sa.Column("last_security_headers", sa.JSON(), nullable=True),
        sa.Column("last_scan_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["last_scan_id"], ["scan_results.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "domain", name="uq_monitoring_user_domain"),
    )
    op.create_index("ix_monitoring_domains_user_id", "monitoring_domains", ["user_id"])
    op.create_index("ix_monitoring_domains_domain", "monitoring_domains", ["domain"])
    op.create_index(
        "ix_monitoring_domains_next_scan_at", "monitoring_domains", ["next_scan_at"]
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    op.create_table(
        "monitoring_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_domain_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=True),
        sa.Column("scan_date", sa.DateTime(), nullable=False),
        sa.Column("scan_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["monitoring_domain_id"], ["monitoring_domains.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["scan_id"], ["scan_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_monitoring_history_domain_id",
        "monitoring_history",
        ["monitoring_domain_id"],
    )


def downgrade() -> None:
    op.drop_table("monitoring_history")
    op.drop_table("notifications")
    op.drop_table("monitoring_domains")
