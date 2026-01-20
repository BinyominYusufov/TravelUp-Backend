"""convert_uuid_to_integer

Revision ID: a7c7b45dae4b
Revises: 5b3568c56080
Create Date: 2026-01-20 18:16:33.658409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c7b45dae4b'
down_revision: Union[str, Sequence[str], None] = '5b3568c56080'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
