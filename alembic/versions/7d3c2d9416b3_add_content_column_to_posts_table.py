"""add content column to posts table

Revision ID: 7d3c2d9416b3
Revises: f5264af2b724
Create Date: 2022-05-27 12:54:59.667258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d3c2d9416b3'
down_revision = 'f5264af2b724'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts',sa.Column('content',sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts','content')
    pass
