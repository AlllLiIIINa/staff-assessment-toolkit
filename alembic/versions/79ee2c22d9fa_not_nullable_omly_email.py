"""not nullable omly email

Revision ID: 79ee2c22d9fa
Revises: fab0b7965cc8
Create Date: 2023-10-17 13:03:09.685483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79ee2c22d9fa'
down_revision: Union[str, None] = 'fab0b7965cc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('users', 'user_firstname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_lastname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.alter_column('users', 'user_hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'user_lastname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'user_firstname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
