"""transaction log table

Revision ID: 9fea1822cbc9
Revises: 0935df5094b3
Create Date: 2021-12-27 11:25:39.645686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fea1822cbc9'
down_revision = '0935df5094b3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tfrom', sa.Unicode(length=200), nullable=False),
        sa.Column('to', sa.Unicode(length=200), nullable=False),
        sa.Column('nft', sa.Unicode(length=200), nullable=False),
        sa.Column('transaction_at', sa.Unicode(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
