"""add lowercase values to saletype

Revision ID: a5f3031d5491
Revises: 96a5a3b1c375
Create Date: 2026-02-19 10:05:37.126832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5f3031d5491'
down_revision = '96a5a3b1c375'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres requires autocommit block for adding enum values
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE saletype ADD VALUE IF NOT EXISTS 'wholesale'")
        op.execute("ALTER TYPE saletype ADD VALUE IF NOT EXISTS 'retail'")

    # Update existing data to use lowercase values so they match the Python Enum
    # We cast to text (::text) to compare with the old uppercase string values
    op.execute("UPDATE transactions SET sale_type = 'retail' WHERE sale_type::text = 'RETAIL'")
    op.execute("UPDATE transactions SET sale_type = 'wholesale' WHERE sale_type::text = 'WHOLESALE'")
    
    op.execute("UPDATE transaction_items SET sale_type = 'retail' WHERE sale_type::text = 'RETAIL'")
    op.execute("UPDATE transaction_items SET sale_type = 'wholesale' WHERE sale_type::text = 'WHOLESALE'")


def downgrade() -> None:
    # Postgres does not support removing enum values easily.
    # We can revert the data to uppercase if needed, but usually we just leave the values.
    op.execute("UPDATE transactions SET sale_type = 'RETAIL' WHERE sale_type::text = 'retail'")
    op.execute("UPDATE transactions SET sale_type = 'WHOLESALE' WHERE sale_type::text = 'wholesale'")
    
    op.execute("UPDATE transaction_items SET sale_type = 'RETAIL' WHERE sale_type::text = 'retail'")
    op.execute("UPDATE transaction_items SET sale_type = 'WHOLESALE' WHERE sale_type::text = 'wholesale'")
