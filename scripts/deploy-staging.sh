#!/bin/bash

# DSRS Staging Deployment Script
# This script deploys the complete DSRS stack to staging environment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="staging"
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.staging.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handling
error_exit() {
    log_error "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose is not installed"
    fi
    
    # Check if environment file exists
    if [[ ! -f "$PROJECT_ROOT/.env.staging" ]]; then
        error_exit "Environment file .env.staging not found. Copy from .env.staging.example and configure."
    fi
    
    log_success "Prerequisites check passed"
}

# Load environment variables
load_environment() {
    log_info "Loading environment variables..."
    
    # Load staging environment
    set -a
    source "$PROJECT_ROOT/.env.staging"
    set +a
    
    # Validate required variables
    required_vars=(
        "POSTGRES_PASSWORD"
        "KONG_PG_PASSWORD"
        "MONGO_ROOT_PASSWORD"
        "KEYCLOAK_ADMIN_PASSWORD"
        "NEXTAUTH_SECRET"
        "KEYCLOAK_CLIENT_SECRET_STAGING"
        "GRAFANA_ADMIN_PASSWORD"
        "JWT_SECRET"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error_exit "Required environment variable $var is not set"
        fi
    done
    
    log_success "Environment variables loaded and validated"
}

# Generate secrets if needed
generate_secrets() {
    log_info "Checking and generating secrets..."
    
    # Create secrets directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/secrets"
    
    # Generate JWT secret if not exists
    if [[ ! -f "$PROJECT_ROOT/secrets/jwt-secret" ]]; then
        openssl rand -base64 32 > "$PROJECT_ROOT/secrets/jwt-secret"
        log_info "Generated JWT secret"
    fi
    
    # Generate NextAuth secret if not exists
    if [[ ! -f "$PROJECT_ROOT/secrets/nextauth-secret" ]]; then
        openssl rand -base64 32 > "$PROJECT_ROOT/secrets/nextauth-secret"
        log_info "Generated NextAuth secret"
    fi
    
    log_success "Secrets check completed"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build all services
    docker-compose $COMPOSE_FILES build --parallel
    
    log_success "Docker images built successfully"
}

# Start infrastructure services
start_infrastructure() {
    log_info "Starting infrastructure services..."
    
    cd "$PROJECT_ROOT"
    
    # Start databases and message queue first
    docker-compose $COMPOSE_FILES up -d postgres mongodb zookeeper kafka
    
    # Wait for databases to be ready
    log_info "Waiting for databases to be ready..."
    sleep 30
    
    # Check database health
    docker-compose $COMPOSE_FILES exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || error_exit "PostgreSQL not ready"
    docker-compose $COMPOSE_FILES exec -T mongodb mongosh --eval "db.adminCommand('ping')" || error_exit "MongoDB not ready"
    
    log_success "Infrastructure services started"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Start microservices temporarily for migrations
    docker-compose $COMPOSE_FILES up -d registry eligibility payment analytics
    
    # Wait for services to be ready
    sleep 20
    
    # Run migrations for each service
    services=("registry" "eligibility" "payment")
    for service in "${services[@]}"; do
        log_info "Running migrations for $service..."
        docker-compose $COMPOSE_FILES exec -T "$service" alembic upgrade head || error_exit "Migration failed for $service"
    done
    
    log_success "Database migrations completed"
}

# Start Kong API Gateway
start_kong() {
    log_info "Starting Kong API Gateway..."
    
    cd "$PROJECT_ROOT"
    
    # Start Kong
    docker-compose $COMPOSE_FILES up -d kong
    
    # Wait for Kong to be ready
    sleep 15
    
    # Check Kong health
    docker-compose $COMPOSE_FILES exec -T kong kong health || error_exit "Kong not healthy"
    
    log_success "Kong API Gateway started"
}

# Start Keycloak
start_keycloak() {
    log_info "Starting Keycloak..."
    
    cd "$PROJECT_ROOT"
    
    # Start Keycloak
    docker-compose $COMPOSE_FILES up -d keycloak
    
    # Wait for Keycloak to be ready
    log_info "Waiting for Keycloak to be ready (this may take a few minutes)..."
    
    # Wait up to 5 minutes for Keycloak to be ready
    timeout=300
    elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if curl -f -s "http://localhost:8080/health/ready" > /dev/null 2>&1; then
            break
        fi
        sleep 10
        elapsed=$((elapsed + 10))
        log_info "Waiting for Keycloak... ($elapsed/$timeout seconds)"
    done
    
    if [[ $elapsed -ge $timeout ]]; then
        error_exit "Keycloak failed to start within $timeout seconds"
    fi
    
    log_success "Keycloak started successfully"
}

# Configure Keycloak
configure_keycloak() {
    log_info "Configuring Keycloak..."
    
    # Run Keycloak configuration script
    if [[ -f "$PROJECT_ROOT/scripts/configure-keycloak.sh" ]]; then
        bash "$PROJECT_ROOT/scripts/configure-keycloak.sh" || error_exit "Keycloak configuration failed"
    else
        log_warning "Keycloak configuration script not found. Manual configuration required."
    fi
    
    log_success "Keycloak configuration completed"
}

# Start monitoring services
start_monitoring() {
    log_info "Starting monitoring services..."
    
    cd "$PROJECT_ROOT"
    
    # Start Prometheus and Grafana
    docker-compose $COMPOSE_FILES up -d prometheus grafana
    
    # Wait for services to be ready
    sleep 15
    
    log_success "Monitoring services started"
}

# Start frontend
start_frontend() {
    log_info "Starting frontend application..."
    
    cd "$PROJECT_ROOT"
    
    # Start web application
    docker-compose $COMPOSE_FILES up -d web
    
    # Wait for frontend to be ready
    sleep 20
    
    # Check frontend health
    if curl -f -s "http://localhost:3000" > /dev/null 2>&1; then
        log_success "Frontend application started successfully"
    else
        log_warning "Frontend may not be fully ready yet"
    fi
}

# Run health checks
run_health_checks() {
    log_info "Running comprehensive health checks..."
    
    cd "$PROJECT_ROOT"
    
    # Check all services
    services=("postgres" "mongodb" "kafka" "kong" "keycloak" "registry" "eligibility" "payment" "analytics" "web")
    
    for service in "${services[@]}"; do
        if docker-compose $COMPOSE_FILES ps "$service" | grep -q "Up"; then
            log_success "$service is running"
        else
            log_error "$service is not running"
        fi
    done
    
    # Test API endpoints
    log_info "Testing API endpoints..."
    
    # Test Kong health
    if curl -f -s "http://localhost:8001/status" > /dev/null 2>&1; then
        log_success "Kong API Gateway is healthy"
    else
        log_error "Kong API Gateway health check failed"
    fi
    
    # Test microservices through Kong
    endpoints=(
        "http://localhost:8000/registry/health"
        "http://localhost:8000/eligibility/health"
        "http://localhost:8000/payment/health"
        "http://localhost:8000/analytics/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            log_success "$(basename "$(dirname "$endpoint")") service is healthy"
        else
            log_warning "$(basename "$(dirname "$endpoint")") service health check failed"
        fi
    done
    
    log_success "Health checks completed"
}

# Display deployment summary
display_summary() {
    log_info "Deployment Summary"
    echo "===================="
    echo "Environment: $ENVIRONMENT"
    echo "Frontend URL: http://localhost:3000"
    echo "API Gateway URL: http://localhost:8000"
    echo "Keycloak URL: http://localhost:8080"
    echo "Grafana URL: http://localhost:3001"
    echo "Prometheus URL: http://localhost:9090"
    echo ""
    echo "Default Credentials:"
    echo "- Keycloak Admin: admin / $KEYCLOAK_ADMIN_PASSWORD"
    echo "- Grafana Admin: admin / $GRAFANA_ADMIN_PASSWORD"
    echo ""
    echo "Next Steps:"
    echo "1. Configure DNS/Load Balancer to point to this server"
    echo "2. Set up SSL certificates"
    echo "3. Configure Keycloak realm and users"
    echo "4. Test end-to-end workflows"
    echo "5. Set up monitoring alerts"
    echo ""
    log_success "DSRS Staging deployment completed successfully!"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    # Add any cleanup tasks here
}

# Trap cleanup function on script exit
trap cleanup EXIT

# Main deployment function
main() {
    log_info "Starting DSRS Staging Deployment"
    echo "=================================="
    
    check_prerequisites
    load_environment
    generate_secrets
    build_images
    start_infrastructure
    run_migrations
    start_kong
    start_keycloak
    configure_keycloak
    start_monitoring
    start_frontend
    run_health_checks
    display_summary
}

# Run main function
main "$@"
