"""rename image to image_url

Revision ID: 96a5a3b1c375
Revises: 8079d3564a62
Create Date: 2026-02-19 09:39:26.211639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96a5a3b1c375'
down_revision = '8079d3564a62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('products', 'image', new_column_name='image_url')

def downgrade() -> None:
    op.alter_column('products', 'image_url', new_column_name='image')
