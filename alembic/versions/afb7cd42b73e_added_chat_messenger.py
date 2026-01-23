"""added chat messenger

Revision ID: afb7cd42b73e
Revises: a7c7b45dae4b
Create Date: 2026-01-23 16:36:22.812284

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afb7cd42b73e'
down_revision: Union[str, Sequence[str], None] = 'a7c7b45dae4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
