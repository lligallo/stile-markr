"""Adding table for tests, removing num_questions from best_marks_table

Revision ID: 3bd1bb6c5852
Revises: 45657277431d
Create Date: 2024-10-14 12:14:28.575966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3bd1bb6c5852'
down_revision: Union[str, None] = '45657277431d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tests',
    sa.Column('test_id', sa.String(length=50), nullable=False),
    sa.Column('num_questions', sa.Integer(), nullable=False),
    sa.Column('import_ids', sa.ARRAY(postgresql.UUID()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),  # Ensure updated_at is always set to the current time on update
    sa.PrimaryKeyConstraint('test_id')
    )
    op.drop_column('best_marks_of_student_per_test', 'num_questions')


def downgrade() -> None:
    op.add_column('best_marks_of_student_per_test', sa.Column('num_questions', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_table('tests')
