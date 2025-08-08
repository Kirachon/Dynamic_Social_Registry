from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'payments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('beneficiary_id', sa.String(length=36), index=True),
        sa.Column('amount', sa.Float()),
        sa.Column('status', sa.String(length=20))
    )

def downgrade():
    op.drop_table('payments')

