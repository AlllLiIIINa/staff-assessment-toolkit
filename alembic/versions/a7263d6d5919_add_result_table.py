"""add_result_table

Revision ID: a7263d6d5919
Revises: fbc6816d472d
Create Date: 2023-11-27 15:02:07.182410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7263d6d5919'
down_revision: Union[str, None] = 'fbc6816d472d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('results',
    sa.Column('result_id', sa.UUID(), nullable=False),
    sa.Column('result_user_id', sa.UUID(), nullable=True),
    sa.Column('result_company_id', sa.UUID(), nullable=True),
    sa.Column('result_quiz_id', sa.UUID(), nullable=True),
    sa.Column('result_created_at', sa.DateTime(), nullable=False),
    sa.Column('result_right_count', sa.Integer(), nullable=True),
    sa.Column('result_total_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['result_company_id'], ['companies.company_id'], ),
    sa.ForeignKeyConstraint(['result_quiz_id'], ['quizzes.quiz_id'], ),
    sa.ForeignKeyConstraint(['result_user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('result_id')
    )
    op.create_index(op.f('ix_results_result_created_at'), 'results', ['result_created_at'], unique=False)
    op.create_index(op.f('ix_results_result_id'), 'results', ['result_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_results_result_id'), table_name='results')
    op.drop_index(op.f('ix_results_result_created_at'), table_name='results')
    op.drop_table('results')
