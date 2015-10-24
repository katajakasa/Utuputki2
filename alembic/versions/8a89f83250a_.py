"""empty message

Revision ID: 8a89f83250a
Revises: 2e683e5273fa
Create Date: 2015-10-24 19:20:03.415000

"""

# revision identifiers, used by Alembic.
revision = '8a89f83250a'
down_revision = '2e683e5273fa'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'visible',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('event', 'visible',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    ### end Alembic commands ###