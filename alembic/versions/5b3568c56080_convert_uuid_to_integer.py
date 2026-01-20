"""convert_uuid_to_integer

Revision ID: 5b3568c56080
Revises: 91e3589e7739
Create Date: 2026-01-20 18:15:46.719232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b3568c56080'
down_revision: Union[str, Sequence[str], None] = '91e3589e7739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - convert UUID to Integer."""
    # Удаляем все данные из зависимых таблиц, так как UUID нельзя конвертировать в Integer
    op.execute("DELETE FROM payments")
    op.execute("DELETE FROM reviews")
    op.execute("DELETE FROM bookings")
    
    # В SQLite нужно удалить таблицы напрямую, так как DROP CONSTRAINT не поддерживается
    # Удаляем старые таблицы (внешние ключи удалятся автоматически)
    op.drop_table('payments')
    op.drop_table('reviews')
    op.drop_table('bookings')
    op.drop_table('destinations')
    
    # Создаем таблицу destinations с Integer ID
    op.create_table('destinations',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('cover_image', sa.String(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу bookings с Integer ID
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('destination_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('travelers_count', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled', name='bookingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу reviews с Integer ID
    op.create_table('reviews',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('destination_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создаем таблицу payments с Integer ID
    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'paid', 'failed', name='paymentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )


def downgrade() -> None:
    """Downgrade schema - convert Integer back to UUID."""
    # Удаляем все данные из зависимых таблиц
    op.execute("DELETE FROM payments")
    op.execute("DELETE FROM reviews")
    op.execute("DELETE FROM bookings")
    
    # В SQLite нужно удалить таблицы напрямую
    # Удаляем таблицы (внешние ключи удалятся автоматически)
    op.drop_table('payments')
    op.drop_table('reviews')
    op.drop_table('bookings')
    op.drop_table('destinations')
    
    # Восстанавливаем таблицы с UUID
    op.create_table('destinations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('cover_image', sa.String(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('bookings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('destination_id', sa.Uuid(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('travelers_count', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled', name='bookingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('reviews',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('destination_id', sa.Uuid(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['destination_id'], ['destinations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('payments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('booking_id', sa.Uuid(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'paid', 'failed', name='paymentstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_id')
    )
