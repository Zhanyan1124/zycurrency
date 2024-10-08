"""added email_verified column to user table

Revision ID: 07876998cb42
Revises: a63f45777a61
Create Date: 2024-04-20 17:04:13.987432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07876998cb42'
down_revision = 'a63f45777a61'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email_verified')

    # ### end Alembic commands ###
