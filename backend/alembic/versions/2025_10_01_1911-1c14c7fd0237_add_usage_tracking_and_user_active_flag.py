"""add_usage_tracking_and_user_active_flag

Revision ID: 1c14c7fd0237
Revises: 5c7a58fe870b
Create Date: 2025-10-01 19:11:27.551516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c14c7fd0237'
down_revision: Union[str, None] = '5c7a58fe870b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active column to users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    
    # Create usage_records table
    op.create_table('usage_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usage_records_user_id'), 'usage_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_usage_records_session_id'), 'usage_records', ['session_id'], unique=False)
    op.create_index(op.f('ix_usage_records_created_at'), 'usage_records', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop usage_records table
    op.drop_index(op.f('ix_usage_records_created_at'), table_name='usage_records')
    op.drop_index(op.f('ix_usage_records_session_id'), table_name='usage_records')
    op.drop_index(op.f('ix_usage_records_user_id'), table_name='usage_records')
    op.drop_table('usage_records')
    
    # Remove is_active column from users table
    op.drop_column('users', 'is_active')


