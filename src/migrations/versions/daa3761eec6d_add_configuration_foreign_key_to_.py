"""Add configuration foreign key to diagnose table

Revision ID: daa3761eec6d
Revises: c730b39f181e
Create Date: 2024-05-14 14:44:20.298699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'daa3761eec6d'
down_revision = 'c730b39f181e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('diagnose', schema=None) as batch_op:
        batch_op.alter_column('task_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'configuration', ['task_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('diagnose', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('task_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
