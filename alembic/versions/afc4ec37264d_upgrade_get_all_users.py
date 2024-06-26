"""upgrade get_all users

Revision ID: afc4ec37264d
Revises: 1e6ed7e313b4
Create Date: 2023-10-03 19:13:55.289503

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'afc4ec37264d'
down_revision: Union[str, None] = '1e6ed7e313b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_users_user_id', table_name='users')
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.create_index('ix_users_user_id', 'users', ['user_id'], unique=False)
