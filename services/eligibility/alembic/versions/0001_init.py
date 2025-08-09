from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'eligibility_decisions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('household_id', sa.String(length=36), index=True),
        sa.Column('status', sa.String(length=20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('eligibility_decisions')

