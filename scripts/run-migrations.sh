#!/bin/bash
set -euo pipefail

# DSRS Database Migration Script
# Runs Alembic migrations for all services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default database URL for local development
DEFAULT_DB_URL="postgresql+psycopg://dsrs:dsrs@localhost:5432/dsrs"
DATABASE_URL=${DATABASE_URL:-$DEFAULT_DB_URL}

echo "🗄️  DSRS Database Migration Runner"
echo "   Database URL: $DATABASE_URL"
echo "   Project Root: $PROJECT_ROOT"
echo ""

# Function to run migrations for a service
run_service_migrations() {
    local service_name=$1
    local service_path="$PROJECT_ROOT/services/$service_name"
    
    echo "📦 Running migrations for $service_name service..."
    
    if [ ! -d "$service_path" ]; then
        echo "   ❌ Service directory not found: $service_path"
        return 1
    fi
    
    if [ ! -f "$service_path/alembic.ini" ]; then
        echo "   ⚠️  No alembic.ini found for $service_name, skipping..."
        return 0
    fi
    
    cd "$service_path"
    
    # Set the database URL for this migration
    export DATABASE_URL="$DATABASE_URL"
    
    # Check current revision
    echo "   📋 Checking current revision..."
    current_revision=$(python -m alembic current 2>/dev/null || echo "none")
    echo "   Current revision: $current_revision"
    
    # Show pending migrations
    echo "   📋 Checking for pending migrations..."
    python -m alembic show head 2>/dev/null || echo "   No migrations found"
    
    # Run migrations
    echo "   🚀 Running migrations..."
    python -m alembic upgrade head
    
    # Show final revision
    final_revision=$(python -m alembic current 2>/dev/null || echo "none")
    echo "   ✅ Final revision: $final_revision"
    echo ""
    
    cd "$PROJECT_ROOT"
}

# Function to validate database connection
validate_database() {
    echo "🔍 Validating database connection..."
    
    # Extract connection details from DATABASE_URL
    # Format: postgresql+psycopg://user:pass@host:port/dbname
    if [[ $DATABASE_URL =~ postgresql\+psycopg://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        local user="${BASH_REMATCH[1]}"
        local host="${BASH_REMATCH[3]}"
        local port="${BASH_REMATCH[4]}"
        local dbname="${BASH_REMATCH[5]}"
        
        echo "   Host: $host:$port"
        echo "   Database: $dbname"
        echo "   User: $user"
        
        # Test connection using psql if available
        if command -v psql >/dev/null 2>&1; then
            echo "   Testing connection..."
            if PGPASSWORD="${BASH_REMATCH[2]}" psql -h "$host" -p "$port" -U "$user" -d "$dbname" -c "SELECT 1;" >/dev/null 2>&1; then
                echo "   ✅ Database connection successful"
            else
                echo "   ❌ Database connection failed"
                return 1
            fi
        else
            echo "   ⚠️  psql not available, skipping connection test"
        fi
    else
        echo "   ⚠️  Could not parse DATABASE_URL format"
    fi
    echo ""
}

# Function to create database if it doesn't exist
ensure_database_exists() {
    echo "🏗️  Ensuring database exists..."
    
    if [[ $DATABASE_URL =~ postgresql\+psycopg://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
        local user="${BASH_REMATCH[1]}"
        local pass="${BASH_REMATCH[2]}"
        local host="${BASH_REMATCH[3]}"
        local port="${BASH_REMATCH[4]}"
        local dbname="${BASH_REMATCH[5]}"
        
        if command -v psql >/dev/null 2>&1; then
            echo "   Creating database '$dbname' if it doesn't exist..."
            PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d postgres -c "CREATE DATABASE $dbname;" 2>/dev/null || echo "   Database already exists or creation failed"
            
            echo "   Creating required extensions..."
            PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$dbname" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null || true
            PGPASSWORD="$pass" psql -h "$host" -p "$port" -U "$user" -d "$dbname" -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";" 2>/dev/null || true
        fi
    fi
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting DSRS database migrations..."
    echo ""
    
    # Validate database connection
    validate_database || {
        echo "❌ Database validation failed. Please check your DATABASE_URL and ensure the database is running."
        exit 1
    }
    
    # Ensure database exists
    ensure_database_exists
    
    # List of services with Alembic migrations
    local services=("registry" "eligibility" "payment")
    
    local failed_services=()
    
    # Run migrations for each service
    for service in "${services[@]}"; do
        if ! run_service_migrations "$service"; then
            failed_services+=("$service")
        fi
    done
    
    # Summary
    echo "📊 Migration Summary:"
    echo "   Services processed: ${#services[@]}"
    echo "   Failed services: ${#failed_services[@]}"
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        echo "   ✅ All migrations completed successfully!"
        exit 0
    else
        echo "   ❌ Failed services: ${failed_services[*]}"
        exit 1
    fi
}

# Run main function
main "$@"
