"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2025-08-09 12:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('household_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=100), nullable=True),
        sa.Column('reference_number', sa.String(length=255), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for performance
    op.create_index('ix_payments_household_id', 'payments', ['household_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_scheduled_date', 'payments', ['scheduled_date'])
    op.create_index('ix_payments_completed_date', 'payments', ['completed_date'])
    op.create_index('ix_payments_reference_number', 'payments', ['reference_number'])
    
    # Create event_outbox table
    op.create_table('event_outbox',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('aggregate_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', sa.Text(), nullable=False),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create indexes on event_outbox
    op.create_index('ix_event_outbox_aggregate_id', 'event_outbox', ['aggregate_id'])
    op.create_index('ix_event_outbox_event_type', 'event_outbox', ['event_type'])
    op.create_index('ix_event_outbox_created_at', 'event_outbox', ['created_at'])
    op.create_index('ix_event_outbox_processed_at', 'event_outbox', ['processed_at'])
    
    # Create processed_events table for idempotency
    op.create_table('processed_events',
        sa.Column('id', sa.String(length=255), nullable=False, primary_key=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('consumer_group', sa.String(length=100), nullable=False, default='payment'),
    )
    
    # Create indexes on processed_events
    op.create_index('ix_processed_events_event_type', 'processed_events', ['event_type'])
    op.create_index('ix_processed_events_consumer_group', 'processed_events', ['consumer_group'])
    op.create_index('ix_processed_events_processed_at', 'processed_events', ['processed_at'])

def downgrade():
    # Drop tables in reverse order
    op.drop_table('processed_events')
    op.drop_table('event_outbox')
    op.drop_table('payments')
