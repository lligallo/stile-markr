"""Create raw import table

Revision ID: 35f2c24c315e
Revises: 
Create Date: 2024-10-12 06:43:40.813611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '35f2c24c315e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('import_vault_raw_imports',
    sa.Column('import_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('origin', sa.String(length=50), nullable=False),
    sa.Column('import_data', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('import_id')
    )


def downgrade() -> None:
    op.drop_table('import_vault_raw_imports')
