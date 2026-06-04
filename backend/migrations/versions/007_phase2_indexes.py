"""Phase 2 performance indexes.

Revision ID: 007_indexes
Revises: 006_phase5
Create Date: 2026-06-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_indexes"
down_revision: Union[str, None] = "006_phase5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_INDEXES = [
    ("scan_results", "ix_scan_results_user_scan_date", ["user_id", "scan_date"]),
    ("scan_results", "ix_scan_results_scan_date", ["scan_date"]),
    ("security_reports", "ix_security_reports_user_created", ["user_id", "created_at"]),
    ("notifications", "ix_notifications_user_read_created", ["user_id", "is_read", "created_at"]),
]


def _existing_indexes(table: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {idx["name"] for idx in inspector.get_indexes(table)}


def upgrade() -> None:
    for table, name, columns in _INDEXES:
        if name not in _existing_indexes(table):
            op.create_index(name, table, columns, unique=False)


def downgrade() -> None:
    for table, name, _columns in reversed(_INDEXES):
        if name in _existing_indexes(table):
            op.drop_index(name, table_name=table)
