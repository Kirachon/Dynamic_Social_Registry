"""align_household_schema_with_current_model

Revision ID: 0003_align_household_schema
Revises: 0002_outbox
Create Date: 2025-08-09 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_align_household_schema'
down_revision = '0002_outbox'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the old households table if it exists (from old schema)
    op.execute("DROP TABLE IF EXISTS households CASCADE")
    
    # Create the new households table with current schema
    op.create_table('households',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('head_of_household_name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('household_size', sa.Integer(), nullable=False, default=1),
        sa.Column('monthly_income', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create indexes for performance
    op.create_index('ix_households_head_of_household_name', 'households', ['head_of_household_name'])
    op.create_index('ix_households_created_at', 'households', ['created_at'])
    op.create_index('ix_households_monthly_income', 'households', ['monthly_income'])
    
    # Update the outbox table to use the correct name (event_outbox)
    op.rename_table('outbox', 'event_outbox')
    
    # Add missing columns to event_outbox if they don't exist
    op.add_column('event_outbox', sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Create indexes on event_outbox for performance
    op.create_index('ix_event_outbox_aggregate_id', 'event_outbox', ['aggregate_id'])
    op.create_index('ix_event_outbox_type', 'event_outbox', ['type'])
    op.create_index('ix_event_outbox_created_at', 'event_outbox', ['created_at'])
    op.create_index('ix_event_outbox_processed_at', 'event_outbox', ['processed_at'])
    
    # Create processed_events table for idempotency
    op.create_table('processed_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('event_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('consumer_group', sa.String(length=100), nullable=False),
    )
    
    # Create indexes on processed_events
    op.create_index('ix_processed_events_event_id', 'processed_events', ['event_id'])
    op.create_index('ix_processed_events_event_type', 'processed_events', ['event_type'])
    op.create_index('ix_processed_events_consumer_group', 'processed_events', ['consumer_group'])


def downgrade():
    # Drop new tables and indexes
    op.drop_table('processed_events')
    
    # Drop indexes from event_outbox
    op.drop_index('ix_event_outbox_processed_at')
    op.drop_index('ix_event_outbox_created_at')
    op.drop_index('ix_event_outbox_type')
    op.drop_index('ix_event_outbox_aggregate_id')
    
    # Remove added column
    op.drop_column('event_outbox', 'processed_at')
    
    # Rename back to outbox
    op.rename_table('event_outbox', 'outbox')
    
    # Drop indexes from households
    op.drop_index('ix_households_monthly_income')
    op.drop_index('ix_households_created_at')
    op.drop_index('ix_households_head_of_household_name')
    
    # Drop the new households table
    op.drop_table('households')
    
    # Recreate the old households table (from 0001_init.py)
    op.create_table('households',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('household_number', sa.String(length=20), unique=True, index=True),
        sa.Column('region_code', sa.String(length=10), index=True),
        sa.Column('pmt_score', sa.Float()),
        sa.Column('status', sa.String(length=20))
    )
