"""add

Revision ID: 508f1f224e22
Revises: afb7cd42b73e
Create Date: 2026-01-23 16:37:20.129773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '508f1f224e22'
down_revision: Union[str, Sequence[str], None] = 'afb7cd42b73e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
