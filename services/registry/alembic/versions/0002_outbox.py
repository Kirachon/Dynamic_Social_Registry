from alembic import op
import sqlalchemy as sa

revision = '0002_outbox'
down_revision = '0001_init'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'outbox',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('aggregate_id', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    op.drop_table('outbox')

