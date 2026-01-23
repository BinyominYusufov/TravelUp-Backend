"""edited images to file

Revision ID: 83ee2c342105
Revises: 8952b21bb324
Create Date: 2026-01-23 17:06:17.343272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83ee2c342105'
down_revision: Union[str, Sequence[str], None] = '8952b21bb324'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
