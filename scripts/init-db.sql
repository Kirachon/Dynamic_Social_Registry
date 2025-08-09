-- Initialize PostgreSQL database for DSRS development
-- This script creates the necessary databases and users for local development

-- Create development database if it doesn't exist
SELECT 'CREATE DATABASE dsrs_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dsrs_dev')\gexec

-- Create test database for running tests
SELECT 'CREATE DATABASE dsrs_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dsrs_test')\gexec

-- Connect to the development database
\c dsrs_dev;

-- Create extensions that might be needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create basic tables for development (these will be managed by Alembic in production)
-- This is just to ensure the database is ready for the services to start

-- Households table (Registry Service)
CREATE TABLE IF NOT EXISTS households (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    head_of_household_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    household_size INTEGER NOT NULL DEFAULT 1,
    monthly_income DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Household members table
CREATE TABLE IF NOT EXISTS household_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    relationship VARCHAR(100),
    is_primary_beneficiary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Eligibility assessments table (Eligibility Service)
CREATE TABLE IF NOT EXISTS eligibility_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id),
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    eligibility_status VARCHAR(50) NOT NULL,
    eligibility_score DECIMAL(5, 2),
    assessment_criteria JSONB,
    assessed_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payment records table (Payment Service)
CREATE TABLE IF NOT EXISTS payment_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id),
    eligibility_assessment_id UUID REFERENCES eligibility_assessments(id),
    payment_amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    transaction_reference VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Event outbox table for saga pattern
CREATE TABLE IF NOT EXISTS event_outbox (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_households_created_at ON households(created_at);
CREATE INDEX IF NOT EXISTS idx_household_members_household_id ON household_members(household_id);
CREATE INDEX IF NOT EXISTS idx_eligibility_assessments_household_id ON eligibility_assessments(household_id);
CREATE INDEX IF NOT EXISTS idx_payment_records_household_id ON payment_records(household_id);
CREATE INDEX IF NOT EXISTS idx_event_outbox_status ON event_outbox(status);
CREATE INDEX IF NOT EXISTS idx_event_outbox_created_at ON event_outbox(created_at);

-- Insert some sample data for development
INSERT INTO households (head_of_household_name, address, phone_number, email, household_size, monthly_income) 
VALUES 
    ('John Doe', '123 Main St, Anytown, ST 12345', '+1-555-0123', 'john.doe@email.com', 4, 2500.00),
    ('Jane Smith', '456 Oak Ave, Somewhere, ST 67890', '+1-555-0456', 'jane.smith@email.com', 2, 1800.00),
    ('Bob Johnson', '789 Pine Rd, Elsewhere, ST 11111', '+1-555-0789', 'bob.johnson@email.com', 3, 3200.00)
ON CONFLICT DO NOTHING;

-- Grant permissions to the development user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev;

-- Connect to test database and set it up similarly
\c dsrs_test;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create the same tables for testing
CREATE TABLE IF NOT EXISTS households (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    head_of_household_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(255),
    household_size INTEGER NOT NULL DEFAULT 1,
    monthly_income DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS household_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    relationship VARCHAR(100),
    is_primary_beneficiary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS eligibility_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id),
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    eligibility_status VARCHAR(50) NOT NULL,
    eligibility_score DECIMAL(5, 2),
    assessment_criteria JSONB,
    assessed_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES households(id),
    eligibility_assessment_id UUID REFERENCES eligibility_assessments(id),
    payment_amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    transaction_reference VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_outbox (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending'
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev;
