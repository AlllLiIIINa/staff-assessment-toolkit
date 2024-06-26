"""add_company_table

Revision ID: dfc9f3af9939
Revises: 79ee2c22d9fa
Create Date: 2023-11-01 17:08:53.672919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfc9f3af9939'
down_revision: Union[str, None] = '79ee2c22d9fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('companies',
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('company_name', sa.String(), nullable=True),
    sa.Column('company_title', sa.String(), nullable=True),
    sa.Column('company_description', sa.String(), nullable=True),
    sa.Column('company_city', sa.String(), nullable=True),
    sa.Column('company_phone', sa.String(), nullable=True),
    sa.Column('company_links', sa.String(), nullable=True),
    sa.Column('company_avatar', sa.String(), nullable=True),
    sa.Column('company_is_visible', sa.Boolean(), nullable=False),
    sa.Column('company_created_at', sa.DateTime(), nullable=False),
    sa.Column('company_updated_at', sa.DateTime(), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('company_id')
    )
    op.create_index(op.f('ix_companies_company_created_at'), 'companies', ['company_created_at'], unique=False)
    op.create_index(op.f('ix_companies_company_id'), 'companies', ['company_id'], unique=True)
    op.create_index(op.f('ix_companies_company_updated_at'), 'companies', ['company_updated_at'], unique=False)
    op.create_table('company_members',
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('company_id', 'user_id')
    )


def downgrade() -> None:
    op.drop_table('company_members')
    op.drop_index(op.f('ix_companies_company_updated_at'), table_name='companies')
    op.drop_index(op.f('ix_companies_company_id'), table_name='companies')
    op.drop_index(op.f('ix_companies_company_created_at'), table_name='companies')
    op.drop_table('companies')
