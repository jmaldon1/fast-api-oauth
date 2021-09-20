"""Added superuser column

Revision ID: 1dbf001035f3
Revises: c56206318903
Create Date: 2021-09-19 00:33:43.723427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dbf001035f3'
down_revision = 'c56206318903'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_superuser')
    # ### end Alembic commands ###
