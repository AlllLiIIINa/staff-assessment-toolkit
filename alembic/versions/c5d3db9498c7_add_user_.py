"""add user_

Revision ID: c5d3db9498c7
Revises: ef9ff957fbbf
Create Date: 2023-10-03 15:22:28.306244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c5d3db9498c7'
down_revision: Union[str, None] = 'ef9ff957fbbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('user_hashed_password', sa.String(), nullable=False))
    op.add_column('users', sa.Column('user_is_superuser', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('user_created_at', sa.DateTime(), nullable=False))
    op.add_column('users', sa.Column('user_updated_at', sa.DateTime(), nullable=False))
    op.alter_column('users', 'user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('users', 'user_email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'user_firstname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'user_lastname',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_updated_at', table_name='users')
    op.create_index(op.f('ix_users_user_created_at'), 'users', ['user_created_at'], unique=False)
    op.create_index(op.f('ix_users_user_updated_at'), 'users', ['user_updated_at'], unique=False)
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'birthday')


def downgrade() -> None:
    op.add_column('users', sa.Column('birthday', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_index(op.f('ix_users_user_updated_at'), table_name='users')
    op.drop_index(op.f('ix_users_user_created_at'), table_name='users')
    op.create_index('ix_users_updated_at', 'users', ['updated_at'], unique=False)
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)
    op.alter_column('users', 'user_lastname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_firstname',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'user_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('users', 'user_updated_at')
    op.drop_column('users', 'user_created_at')
    op.drop_column('users', 'user_is_superuser')
    op.drop_column('users', 'user_hashed_password')
