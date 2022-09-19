"""Rename column in Context

Revision ID: 9ee534d043cb
Revises: 5266868c2621
Create Date: 2022-06-13 08:34:34.620656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ee534d043cb'
down_revision = '5266868c2621'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('context', sa.Column('encoded_password', sa.String(), nullable=False))
    op.drop_column('context', 'hashed_password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('context', sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('context', 'encoded_password')
    # ### end Alembic commands ###
