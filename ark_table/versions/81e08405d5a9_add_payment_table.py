"""add payment table

Revision ID: 81e08405d5a9
Revises: 9fea1822cbc9
Create Date: 2021-12-28 13:25:08.168652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81e08405d5a9'
down_revision = '9fea1822cbc9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('payment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.String(100), nullable=False),
        sa.Column('transaction_id', sa.String(200), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('create_at', sa.String(length=200), nullable=False),
        sa.Column('line_id', sa.String(200), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('payment')
