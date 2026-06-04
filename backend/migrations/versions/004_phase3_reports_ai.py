"""Phase 3 — AI fields and security_reports.

Revision ID: 004_phase3
Revises: 003_phase2
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_phase3"
down_revision: Union[str, None] = "003_phase2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("scan_results", sa.Column("ai_summary", sa.Text(), nullable=True))
    op.add_column(
        "scan_results", sa.Column("ai_risk_assessment", sa.JSON(), nullable=True)
    )
    op.add_column(
        "scan_results", sa.Column("ai_recommendations", sa.JSON(), nullable=True)
    )

    op.create_table(
        "security_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("scan_id", sa.BigInteger(), nullable=False),
        sa.Column("report_name", sa.String(length=255), nullable=False),
        sa.Column("report_path", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scan_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_security_reports_user_id"), "security_reports", ["user_id"]
    )
    op.create_index(
        op.f("ix_security_reports_scan_id"), "security_reports", ["scan_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_security_reports_scan_id"), table_name="security_reports")
    op.drop_index(op.f("ix_security_reports_user_id"), table_name="security_reports")
    op.drop_table("security_reports")
    op.drop_column("scan_results", "ai_recommendations")
    op.drop_column("scan_results", "ai_risk_assessment")
    op.drop_column("scan_results", "ai_summary")
