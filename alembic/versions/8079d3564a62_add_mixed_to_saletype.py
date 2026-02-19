"""add mixed to saletype

Revision ID: 8079d3564a62
Revises: e4a227be4a08
Create Date: 2026-02-19 09:36:09.711605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8079d3564a62'
down_revision = 'e4a227be4a08'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres requires autocommit block for adding enum values
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE saletype ADD VALUE IF NOT EXISTS 'mixed'")

def downgrade() -> None:
    # Postgres does not support removing enum values easily, so we do nothing
    pass

