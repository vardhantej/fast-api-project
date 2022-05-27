"""create posts table

Revision ID: f5264af2b724
Revises: 
Create Date: 2022-05-27 11:59:24.770854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5264af2b724'
down_revision = None
branch_labels = None
depends_on = None

# handles changes
def upgrade():
    op.create_table('posts',sa.Column('id',sa.Integer(), nullable=False, primary_key=True), sa.Column('title', sa.String(), nullable=False))
    pass

# handles rolling back changes
def downgrade():
    op.drop_table('posts')
    pass
