"""Add status

Revision ID: 87175b2f4230
Revises: fe640de1398a
Create Date: 2024-05-26 21:51:54.180784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87175b2f4230'
down_revision = 'fe640de1398a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Integer(), nullable=False))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('unlocked_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('unlocked_at')
        batch_op.drop_column('status')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###