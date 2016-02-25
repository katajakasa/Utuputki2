"""Add missing constraints

Revision ID: 3a872ea246b9
Revises: 4690204e5a62
Create Date: 2015-10-28 19:00:20.176000

"""

# revision identifiers, used by Alembic.
revision = '3a872ea246b9'
down_revision = '4690204e5a62'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.alter_column('event', 'visible',
                    existing_type=mysql.TINYINT(display_width=1),
                    type_=sa.Boolean(),
                    existing_nullable=True)
    op.add_column('sourcequeue', sa.Column('target', sa.Integer(), nullable=True))
    op.create_unique_constraint('_user_target_uc', 'sourcequeue', ['user', 'target'])
    op.create_foreign_key(None, 'sourcequeue', 'player', ['target'], ['id'])


def downgrade():
    op.drop_constraint(None, 'sourcequeue', type_='foreignkey')
    op.drop_constraint('_user_target_uc', 'sourcequeue', type_='unique')
    op.drop_column('sourcequeue', 'target')
    op.alter_column('event',
                    'visible',
                    existing_type=sa.Boolean(),
                    type_=mysql.TINYINT(display_width=1),
                    existing_nullable=True)
