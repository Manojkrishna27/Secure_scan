"""Phase 2 — scan_results table.

Revision ID: 003_phase2
Revises: 002_phase1
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_phase2"
down_revision: Union[str, None] = "002_phase1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scan_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("ssl_status", sa.String(length=32), nullable=True),
        sa.Column("issuer", sa.String(length=512), nullable=True),
        sa.Column("common_name", sa.String(length=255), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("days_remaining", sa.Integer(), nullable=True),
        sa.Column("tls_version", sa.String(length=32), nullable=True),
        sa.Column("security_score", sa.Integer(), nullable=True),
        sa.Column("risk_level", sa.String(length=32), nullable=True),
        sa.Column("grade", sa.String(length=8), nullable=True),
        sa.Column("scan_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("organization", sa.String(length=512), nullable=True),
        sa.Column("serial_number", sa.String(length=128), nullable=True),
        sa.Column("signature_algorithm", sa.String(length=128), nullable=True),
        sa.Column("certificate_version", sa.String(length=32), nullable=True),
        sa.Column("public_key_algorithm", sa.String(length=64), nullable=True),
        sa.Column("domain_name", sa.String(length=255), nullable=True),
        sa.Column("tls_versions", sa.JSON(), nullable=True),
        sa.Column("certificate_chain", sa.JSON(), nullable=True),
        sa.Column("security_headers", sa.JSON(), nullable=True),
        sa.Column("header_values", sa.JSON(), nullable=True),
        sa.Column("findings", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scan_results_user_id"), "scan_results", ["user_id"])
    op.create_index(op.f("ix_scan_results_domain"), "scan_results", ["domain"])


def downgrade() -> None:
    op.drop_index(op.f("ix_scan_results_domain"), table_name="scan_results")
    op.drop_index(op.f("ix_scan_results_user_id"), table_name="scan_results")
    op.drop_table("scan_results")
