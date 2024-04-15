"""add birthday

Revision ID: 1e6ed7e313b4
Revises: c5d3db9498c7
Create Date: 2023-10-03 15:26:23.052401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e6ed7e313b4'
down_revision: Union[str, None] = 'c5d3db9498c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_birthday', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'user_birthday')
