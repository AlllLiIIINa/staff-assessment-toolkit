"""add notification table

Revision ID: dc6e69353519
Revises: a7263d6d5919
Create Date: 2023-12-13 17:24:39.467936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc6e69353519'
down_revision: Union[str, None] = 'a7263d6d5919'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('company_notifications',
    sa.Column('notification_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('notification_status', sa.Boolean(), nullable=True),
    sa.Column('notification_text', sa.String(), nullable=True),
    sa.Column('notification_created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('notification_id', 'user_id', 'company_id')
    )
    op.create_index(op.f('ix_company_notifications_notification_created_at'), 'company_notifications', ['notification_created_at'], unique=False)
    op.create_index(op.f('ix_company_notifications_notification_id'), 'company_notifications', ['notification_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_company_notifications_notification_id'), table_name='company_notifications')
    op.drop_index(op.f('ix_company_notifications_notification_created_at'), table_name='company_notifications')
    op.drop_table('company_notifications')
