"""upgrade user model

Revision ID: e7540b01de67
Revises: afc4ec37264d
Create Date: 2023-10-03 22:06:34.778939

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'e7540b01de67'
down_revision: Union[str, None] = 'afc4ec37264d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
