"""Table best scores with traceability

Revision ID: 3bd290a3a542
Revises: 35f2c24c315e
Create Date: 2024-10-14 00:11:30.882936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3bd290a3a542'
down_revision: Union[str, None] = '35f2c24c315e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('best_marks_of_student_per_test',
    sa.Column('student_id', sa.String(length=50), nullable=False),
    sa.Column('test_id', sa.String(length=50), nullable=False),
    sa.Column('num_questions', sa.Integer(), nullable=False),
    sa.Column('num_correct', sa.Integer(), nullable=False),
    sa.Column('import_ids', sa.ARRAY(postgresql.UUID()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),  # Ensure updated_at is always set to the current time on update
    sa.PrimaryKeyConstraint('student_id', 'test_id')
    )


def downgrade() -> None:
    op.drop_table('best_marks_of_student_per_test')
