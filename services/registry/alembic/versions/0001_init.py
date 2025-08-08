from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'households',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('household_number', sa.String(length=20), unique=True, index=True),
        sa.Column('region_code', sa.String(length=10), index=True),
        sa.Column('pmt_score', sa.Float()),
        sa.Column('status', sa.String(length=20))
    )

def downgrade():
    op.drop_table('households')

