"""add_quiz_question_tables

Revision ID: b732383860cf
Revises: e9c54e9a242b
Create Date: 2023-11-13 12:55:09.486340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b732383860cf'
down_revision: Union[str, None] = 'e9c54e9a242b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('quizzes',
    sa.Column('quiz_id', sa.UUID(), nullable=False),
    sa.Column('quiz_name', sa.String(), nullable=True),
    sa.Column('quiz_title', sa.String(), nullable=True),
    sa.Column('quiz_description', sa.String(), nullable=True),
    sa.Column('quiz_frequency', sa.Integer(), nullable=True),
    sa.Column('company_id', sa.UUID(), nullable=True),
    sa.Column('quiz_created_by', sa.UUID(), nullable=True),
    sa.Column('quiz_updated_by', sa.UUID(), nullable=True),
    sa.Column('quiz_created_at', sa.DateTime(), nullable=False),
    sa.Column('quiz_updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'], ),
    sa.PrimaryKeyConstraint('quiz_id')
    )
    op.create_index(op.f('ix_quizzes_quiz_created_at'), 'quizzes', ['quiz_created_at'], unique=False)
    op.create_index(op.f('ix_quizzes_quiz_id'), 'quizzes', ['quiz_id'], unique=True)
    op.create_index(op.f('ix_quizzes_quiz_updated_at'), 'quizzes', ['quiz_updated_at'], unique=False)
    op.create_table('questions',
    sa.Column('question_id', sa.UUID(), nullable=False),
    sa.Column('question_text', sa.String(), nullable=True),
    sa.Column('question_answers', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('question_correct_answer', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('quiz_id', sa.UUID(), nullable=True),
    sa.Column('question_company_id', sa.UUID(), nullable=True),
    sa.Column('question_created_by', sa.UUID(), nullable=True),
    sa.Column('question_updated_by', sa.UUID(), nullable=True),
    sa.Column('question_created_at', sa.DateTime(), nullable=False),
    sa.Column('question_updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['question_company_id'], ['companies.company_id'], ),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.quiz_id'], ),
    sa.PrimaryKeyConstraint('question_id')
    )
    op.create_index(op.f('ix_questions_question_created_at'), 'questions', ['question_created_at'], unique=False)
    op.create_index(op.f('ix_questions_question_id'), 'questions', ['question_id'], unique=True)
    op.create_index(op.f('ix_questions_question_updated_at'), 'questions', ['question_updated_at'], unique=False)
    op.create_unique_constraint(None, 'companies', ['company_name'])


def downgrade() -> None:
    op.drop_constraint(None, 'companies', type_='unique')
    op.drop_index(op.f('ix_questions_question_updated_at'), table_name='questions')
    op.drop_index(op.f('ix_questions_question_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_question_created_at'), table_name='questions')
    op.drop_table('questions')
    op.drop_index(op.f('ix_quizzes_quiz_updated_at'), table_name='quizzes')
    op.drop_index(op.f('ix_quizzes_quiz_id'), table_name='quizzes')
    op.drop_index(op.f('ix_quizzes_quiz_created_at'), table_name='quizzes')
    op.drop_table('quizzes')
