"""add_companyinvitations_table

Revision ID: e9c54e9a242b
Revises: dfc9f3af9939
Create Date: 2023-11-06 23:36:16.735845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9c54e9a242b'
down_revision: Union[str, None] = 'dfc9f3af9939'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('company_invitations',
    sa.Column('invitation_id', sa.UUID(), nullable=False),
    sa.Column('sender_id', sa.UUID(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=False),
    sa.Column('company_id', sa.UUID(), nullable=False),
    sa.Column('invitation_created_at', sa.DateTime(), nullable=False),
    sa.Column('invitation_updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('invitation_id')
    )
    op.create_index(op.f('ix_company_invitations_invitation_created_at'), 'company_invitations', ['invitation_created_at'], unique=False)
    op.create_index(op.f('ix_company_invitations_invitation_id'), 'company_invitations', ['invitation_id'], unique=True)
    op.create_index(op.f('ix_company_invitations_invitation_updated_at'), 'company_invitations', ['invitation_updated_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_company_invitations_invitation_updated_at'), table_name='company_invitations')
    op.drop_index(op.f('ix_company_invitations_invitation_id'), table_name='company_invitations')
    op.drop_index(op.f('ix_company_invitations_invitation_created_at'), table_name='company_invitations')
    op.drop_table('company_invitations')
