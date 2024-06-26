"""add avatar

Revision ID: ac2177eee842
Revises: 87175b2f4230
Create Date: 2024-05-27 20:31:54.280387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac2177eee842'
down_revision = '87175b2f4230'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('avatar_id', sa.String(length=100), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_users_avatar_id_images'), 'images', ['avatar_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_users_avatar_id_images'), type_='foreignkey')
        batch_op.drop_column('avatar_id')

    # ### end Alembic commands ###
