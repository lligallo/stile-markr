"""Adding test_id index

Revision ID: 45657277431d
Revises: 3bd290a3a542
Create Date: 2024-10-14 03:46:22.614936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45657277431d'
down_revision: Union[str, None] = '3bd290a3a542'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('idx_test_id', 'best_marks_of_student_per_test', ['test_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_test_id', table_name='best_marks_of_student_per_test')
