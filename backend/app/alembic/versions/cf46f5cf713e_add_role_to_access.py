"""Add role to access

Revision ID: cf46f5cf713e
Revises: bb6c5e4149a0
Create Date: 2022-07-01 10:39:21.967707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf46f5cf713e'
down_revision = 'bb6c5e4149a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('access', sa.Column('role', sa.String(), nullable=True))
    op.create_index(op.f('ix_access_role'), 'access', ['role'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_access_role'), table_name='access')
    op.drop_column('access', 'role')
    # ### end Alembic commands ###
