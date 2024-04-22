"""change user id to user email in configuration table 

Revision ID: 8f59b99351a3
Revises: d126cdd7b0f1
Create Date: 2024-04-22 14:15:52.775353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f59b99351a3'
down_revision = 'd126cdd7b0f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('configuration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_email', sa.String(), nullable=True))
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('configuration', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_column('user_email')

    # ### end Alembic commands ###
