"""add superuser

Revision ID: 51dfa236bcf1
Revises: 1baf7a0c6aab
Create Date: 2021-12-13 23:00:51.552018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51dfa236bcf1'
down_revision = '1baf7a0c6aab'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users', sa.Column('is_superuser', sa.Boolean(), default=False, nullable=False)
    )


def downgrade():
    op.drop_column(
        'users', 'is_superuser'
    )
