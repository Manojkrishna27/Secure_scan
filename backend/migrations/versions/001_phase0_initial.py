"""Phase 0 initial — empty schema baseline.

Revision ID: 001_phase0
Revises:
Create Date: 2026-06-01

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001_phase0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
