"""generate user_id

Revision ID: fab0b7965cc8
Revises: e7540b01de67
Create Date: 2023-10-04 22:14:58.468286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fab0b7965cc8'
down_revision: Union[str, None] = 'e7540b01de67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_id_new', sa.UUID))

    op.execute("UPDATE users SET user_id_new = CAST(user_id AS UUID)")

    op.drop_column('users', 'user_id')

    op.alter_column('users', 'user_id_new', new_column_name='user_id')
    op.alter_column('users', 'user_id',
               existing_type=sa.VARCHAR(),
               type_=sa.UUID(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('users_user_id_seq'::regclass)"))


def downgrade() -> None:
    op.alter_column('users', 'user_id',
               existing_type=sa.UUID(),
               type_=sa.VARCHAR(),
               existing_nullable=False,
               existing_server_default=sa.text("nextval('users_user_id_seq'::regclass)"))
