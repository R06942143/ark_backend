"""alert table 

Revision ID: 1baf7a0c6aab
Revises: e33bf2621069
Create Date: 2021-12-13 16:28:02.806559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1baf7a0c6aab'
down_revision = 'e33bf2621069'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('nft',
        sa.Column('category', sa.String(10))
    )
    op.add_column('nft',
        sa.Column('is_active', sa.Boolean(), default=False, nullable=False)
    )

def downgrade():
    op.drop_column('nft', 'category')
    op.drop_column('nft', 'is_actived')
