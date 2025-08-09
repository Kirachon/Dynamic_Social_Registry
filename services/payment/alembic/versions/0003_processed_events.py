from alembic import op
import sqlalchemy as sa

revision = '0003_processed_events'
down_revision = '0002_outbox'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'processed_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('processed_events')

