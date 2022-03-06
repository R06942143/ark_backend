"""fix typos

Revision ID: 0935df5094b3
Revises: 51dfa236bcf1
Create Date: 2021-12-24 15:22:26.954039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0935df5094b3'
down_revision = '51dfa236bcf1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nft',
        sa.Column('is_active', sa.Boolean(), default=False, nullable=False)
    )

def downgrade():
    op.drop_column('nft', 'is_active')
