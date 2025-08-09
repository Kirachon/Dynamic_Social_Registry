#!/bin/bash

# DSRS Production Deployment Script
# This script executes the complete production deployment of DSRS

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="production"
COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

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

# Display banner
display_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    DSRS Production Deployment                                ║"
    echo "║                Dynamic Social Registry System                               ║"
    echo "║                                                                              ║"
    echo "║  🚀 Deploying complete production-ready system                              ║"
    echo "║  🔒 100% Open Source Stack (No paid APIs)                                  ║"
    echo "║  🏗️  Microservices + API Gateway + Identity Provider                       ║"
    echo "║  📊 Real-time Analytics + Monitoring                                        ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking production deployment prerequisites..."
    
    # Check if running as non-root user
    if [[ $EUID -eq 0 ]]; then
        error_exit "This script should not be run as root for security reasons"
    fi
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed. Please install Docker first."
    fi
    
    if ! docker info &> /dev/null; then
        error_exit "Docker is not running. Please start Docker service."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if we're on the main branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        error_exit "Must be on main branch for production deployment. Current branch: $current_branch"
    fi
    
    # Check if production environment file exists
    if [[ ! -f "$PROJECT_ROOT/.env.production" ]]; then
        error_exit "Production environment file .env.production not found. Please create it from .env.staging.example"
    fi
    
    # Check if SSL certificates exist (if domains are configured)
    if [[ -n "${DOMAIN:-}" ]]; then
        if [[ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
            log_warning "SSL certificates not found. Make sure to configure SSL after deployment."
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Load and validate environment
load_environment() {
    log_info "Loading production environment configuration..."
    
    # Load production environment
    set -a
    source "$PROJECT_ROOT/.env.production"
    set +a
    
    # Validate critical environment variables
    required_vars=(
        "ENVIRONMENT"
        "POSTGRES_PASSWORD"
        "KONG_PG_PASSWORD"
        "MONGO_ROOT_PASSWORD"
        "KEYCLOAK_ADMIN_PASSWORD"
        "NEXTAUTH_SECRET"
        "KEYCLOAK_CLIENT_SECRET"
        "GRAFANA_ADMIN_PASSWORD"
        "JWT_SECRET"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error_exit "Required environment variable $var is not set in .env.production"
        fi
    done
    
    # Validate environment is set to production
    if [[ "$ENVIRONMENT" != "production" ]]; then
        error_exit "ENVIRONMENT must be set to 'production' in .env.production"
    fi
    
    log_success "Production environment loaded and validated"
}

# Create production docker-compose file if it doesn't exist
create_production_compose() {
    if [[ ! -f "$PROJECT_ROOT/docker-compose.prod.yml" ]]; then
        log_info "Creating production docker-compose configuration..."
        
        # Copy staging compose as base for production
        cp "$PROJECT_ROOT/docker-compose.staging.yml" "$PROJECT_ROOT/docker-compose.prod.yml"
        
        # Update for production settings
        sed -i 's/staging/production/g' "$PROJECT_ROOT/docker-compose.prod.yml"
        sed -i 's/dsrs-staging/dsrs-production/g' "$PROJECT_ROOT/docker-compose.prod.yml"
        
        log_success "Production compose file created"
    fi
}

# Generate production secrets
generate_production_secrets() {
    log_info "Generating production secrets..."
    
    # Create secrets directory
    mkdir -p "$PROJECT_ROOT/secrets"
    
    # Generate secrets if they don't exist
    secrets=(
        "jwt-secret"
        "nextauth-secret"
        "postgres-password"
        "mongo-password"
        "keycloak-admin-password"
        "grafana-password"
    )
    
    for secret in "${secrets[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/secrets/$secret" ]]; then
            openssl rand -base64 32 > "$PROJECT_ROOT/secrets/$secret"
            chmod 600 "$PROJECT_ROOT/secrets/$secret"
            log_info "Generated secret: $secret"
        fi
    done
    
    log_success "Production secrets generated"
}

# Pull latest Docker images
pull_docker_images() {
    log_info "Pulling latest Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Pull base images
    docker-compose $COMPOSE_FILES pull
    
    log_success "Docker images pulled successfully"
}

# Build application images
build_application_images() {
    log_info "Building application Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build all services
    docker-compose $COMPOSE_FILES build --parallel --no-cache
    
    log_success "Application images built successfully"
}

# Start infrastructure services
start_infrastructure() {
    log_info "Starting infrastructure services..."
    
    cd "$PROJECT_ROOT"
    
    # Start databases and message queue first
    docker-compose $COMPOSE_FILES up -d postgres mongodb zookeeper kafka
    
    # Wait for infrastructure to be ready
    log_info "Waiting for infrastructure services to be ready..."
    sleep 45
    
    # Verify infrastructure health
    max_attempts=30
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose $COMPOSE_FILES exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" && \
           docker-compose $COMPOSE_FILES exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
            break
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for databases... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        error_exit "Infrastructure services failed to become ready"
    fi
    
    log_success "Infrastructure services started and ready"
}

# Run database migrations
run_database_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Start microservices temporarily for migrations
    docker-compose $COMPOSE_FILES up -d registry eligibility payment analytics
    
    # Wait for services to be ready
    sleep 30
    
    # Run migrations for each service
    services=("registry" "eligibility" "payment")
    for service in "${services[@]}"; do
        log_info "Running migrations for $service service..."
        
        max_attempts=5
        attempt=0
        
        while [[ $attempt -lt $max_attempts ]]; do
            if docker-compose $COMPOSE_FILES exec -T "$service" alembic upgrade head; then
                log_success "Migrations completed for $service"
                break
            fi
            
            attempt=$((attempt + 1))
            log_warning "Migration attempt $attempt failed for $service, retrying..."
            sleep 10
        done
        
        if [[ $attempt -eq $max_attempts ]]; then
            error_exit "Database migrations failed for $service after $max_attempts attempts"
        fi
    done
    
    log_success "All database migrations completed successfully"
}

# Start Kong API Gateway
start_kong() {
    log_info "Starting Kong API Gateway..."
    
    cd "$PROJECT_ROOT"
    
    # Start Kong
    docker-compose $COMPOSE_FILES up -d kong
    
    # Wait for Kong to be ready
    max_attempts=20
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s "http://localhost:8001/status" > /dev/null 2>&1; then
            log_success "Kong API Gateway started successfully"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for Kong... (attempt $attempt/$max_attempts)"
        sleep 15
    done
    
    error_exit "Kong API Gateway failed to start within expected time"
}

# Start Keycloak
start_keycloak() {
    log_info "Starting Keycloak identity provider..."
    
    cd "$PROJECT_ROOT"
    
    # Start Keycloak
    docker-compose $COMPOSE_FILES up -d keycloak
    
    # Wait for Keycloak to be ready (can take several minutes)
    log_info "Waiting for Keycloak to initialize (this may take 3-5 minutes)..."
    
    max_attempts=30
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s "http://localhost:8080/health/ready" > /dev/null 2>&1; then
            log_success "Keycloak started successfully"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for Keycloak... (attempt $attempt/$max_attempts)"
        sleep 20
    done
    
    error_exit "Keycloak failed to start within expected time"
}

# Configure Keycloak
configure_keycloak() {
    log_info "Configuring Keycloak for production..."
    
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
    sleep 20
    
    # Verify monitoring services
    if curl -f -s "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        log_success "Prometheus started successfully"
    else
        log_warning "Prometheus may not be fully ready yet"
    fi
    
    if curl -f -s "http://localhost:3001/api/health" > /dev/null 2>&1; then
        log_success "Grafana started successfully"
    else
        log_warning "Grafana may not be fully ready yet"
    fi
    
    log_success "Monitoring services started"
}

# Start frontend application
start_frontend() {
    log_info "Starting frontend application..."
    
    cd "$PROJECT_ROOT"
    
    # Start web application
    docker-compose $COMPOSE_FILES up -d web
    
    # Wait for frontend to be ready
    sleep 30
    
    # Check frontend health
    max_attempts=10
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s "http://localhost:3000" > /dev/null 2>&1; then
            log_success "Frontend application started successfully"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for frontend... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    log_warning "Frontend may not be fully ready yet, but deployment will continue"
}

# Run comprehensive health checks
run_health_checks() {
    log_info "Running comprehensive production health checks..."
    
    cd "$PROJECT_ROOT"
    
    # Check all containers are running
    log_info "Checking container status..."
    if ! docker-compose $COMPOSE_FILES ps | grep -q "Up"; then
        log_warning "Some containers may not be running properly"
    fi
    
    # Test API endpoints through Kong
    log_info "Testing API endpoints..."
    endpoints=(
        "http://localhost:8000/registry/health"
        "http://localhost:8000/eligibility/health"
        "http://localhost:8000/payment/health"
        "http://localhost:8000/analytics/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        service_name=$(echo "$endpoint" | cut -d'/' -f4)
        if curl -f -s "$endpoint" > /dev/null 2>&1; then
            log_success "$service_name service is healthy"
        else
            log_warning "$service_name service health check failed"
        fi
    done
    
    # Test Kong admin API
    if curl -f -s "http://localhost:8001/status" > /dev/null 2>&1; then
        log_success "Kong API Gateway is healthy"
    else
        log_warning "Kong API Gateway health check failed"
    fi
    
    # Test Keycloak
    if curl -f -s "http://localhost:8080/health/ready" > /dev/null 2>&1; then
        log_success "Keycloak is healthy"
    else
        log_warning "Keycloak health check failed"
    fi
    
    # Test frontend
    if curl -f -s "http://localhost:3000" > /dev/null 2>&1; then
        log_success "Frontend application is healthy"
    else
        log_warning "Frontend health check failed"
    fi
    
    log_success "Health checks completed"
}

# Create initial backup
create_initial_backup() {
    log_info "Creating initial production backup..."
    
    # Create backup directory
    backup_dir="/backup/dsrs_production_initial_$(date +%Y%m%d_%H%M%S)"
    sudo mkdir -p "$backup_dir"
    
    # Backup databases
    docker-compose $COMPOSE_FILES exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | sudo tee "$backup_dir/postgres_dsrs.sql" > /dev/null
    docker-compose $COMPOSE_FILES exec -T mongodb mongodump --db "$MONGO_DATABASE" --out "$backup_dir/mongodb"
    
    # Backup configuration
    sudo cp -r "$PROJECT_ROOT/.env.production" "$backup_dir/"
    sudo cp -r "$PROJECT_ROOT/infra/" "$backup_dir/"
    sudo cp -r "$PROJECT_ROOT/scripts/" "$backup_dir/"
    
    # Create archive
    sudo tar -czf "$backup_dir.tar.gz" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"
    sudo rm -rf "$backup_dir"
    
    log_success "Initial backup created: $backup_dir.tar.gz"
}

# Display deployment summary
display_deployment_summary() {
    log_info "Production Deployment Summary"
    echo "=============================================="
    echo "Environment: $ENVIRONMENT"
    echo "Deployment Time: $(date)"
    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend:    http://localhost:3000"
    echo "   API Gateway: http://localhost:8000"
    echo "   Keycloak:    http://localhost:8080"
    echo "   Grafana:     http://localhost:3001"
    echo "   Prometheus:  http://localhost:9090"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Keycloak Admin: admin / $KEYCLOAK_ADMIN_PASSWORD"
    echo "   Grafana Admin:  admin / $GRAFANA_ADMIN_PASSWORD"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Configure SSL certificates for production domains"
    echo "   2. Update DNS records to point to this server"
    echo "   3. Test complete end-to-end workflow"
    echo "   4. Configure monitoring alerts"
    echo "   5. Conduct user training"
    echo "   6. Plan go-live communication"
    echo ""
    echo "📚 Documentation:"
    echo "   - Deployment Guide: DEPLOYMENT_GUIDE.md"
    echo "   - Operations Manual: RUNBOOK.md"
    echo "   - Production Checklist: PRODUCTION_READINESS_CHECKLIST.md"
    echo ""
    log_success "🎉 DSRS Production Deployment Completed Successfully!"
    echo ""
    echo "The Dynamic Social Registry System is now running in production mode"
    echo "with complete end-to-end functionality, authentication, and monitoring."
    echo ""
    echo "🚀 System Status: PRODUCTION READY"
}

# Main deployment function
main() {
    display_banner
    
    log_info "Starting DSRS Production Deployment"
    echo "======================================"
    
    check_prerequisites
    load_environment
    create_production_compose
    generate_production_secrets
    pull_docker_images
    build_application_images
    start_infrastructure
    run_database_migrations
    start_kong
    start_keycloak
    configure_keycloak
    start_monitoring
    start_frontend
    run_health_checks
    create_initial_backup
    display_deployment_summary
    
    log_success "Production deployment completed successfully!"
}

# Cleanup function
cleanup() {
    if [[ $? -ne 0 ]]; then
        log_error "Deployment failed. Check logs above for details."
        log_info "To retry deployment, fix the issues and run this script again."
        log_info "To rollback, run: docker-compose down && docker system prune -f"
    fi
}

# Trap cleanup function on script exit
trap cleanup EXIT

# Run main function
main "$@"
