"""alert table 

Revision ID: e33bf2621069
Revises: 
Create Date: 2021-12-13 16:02:15.900470

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e33bf2621069'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users', sa.Column('is_active', sa.Boolean(), default=False, nullable=False)
    )
    op.add_column(
        'users', sa.Column('created_at', sa.types.DateTime(timezone=True), default=datetime.now(), nullable=False)
    )
    op.add_column(
        'users', sa.Column('updated_at', sa.types.DateTime(timezone=True), default=datetime.now(), nullable=False)
    )
    op.add_column(
        'users', sa.Column('hashed_password', sa.String(60), nullable=False)
    )
    op.add_column(
        'users', sa.Column('email', sa.String(100), nullable=False)
    )
    op.add_column(
        'users', sa.Column('account', sa.String(50), nullable=False)
    )


def downgrade():
    op.drop_column('users',
    'is_active'
    )
    op.drop_column('users',
    'created_at'
    )
    op.drop_column('users',
    'updated_at'
    )
    op.drop_column('users',
    'hashed_password'
    )
    op.drop_column('users',
    'email'
    )
    op.drop_column('users',
    'account'
    )
