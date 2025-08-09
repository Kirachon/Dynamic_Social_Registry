#!/bin/bash

# DSRS Development Deployment Script
# This script deploys the DSRS system using the lightweight development configuration

set -e  # Exit on any error

echo "🚀 Starting DSRS Development Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker availability..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check if Docker Compose is available
print_status "Checking Docker Compose availability..."
if ! docker compose version > /dev/null 2>&1; then
    print_error "Docker Compose is not available. Please install Docker Compose and try again."
    exit 1
fi
print_success "Docker Compose is available"

# Clean up any existing containers
print_status "Cleaning up existing containers..."
docker compose -f docker-compose.dev.yml down --volumes --remove-orphans 2>/dev/null || true
print_success "Cleanup completed"

# Build and start infrastructure services first
print_status "Starting infrastructure services (PostgreSQL, Redpanda, MongoDB, Redis)..."
docker compose -f docker-compose.dev.yml up -d postgres redpanda mongodb redis

# Wait for infrastructure services to be healthy
print_status "Waiting for infrastructure services to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker compose -f docker-compose.dev.yml ps --format json | jq -r '.[].Health' | grep -q "unhealthy"; then
        print_warning "Some services are still starting... (attempt $((attempt + 1))/$max_attempts)"
        sleep 5
        attempt=$((attempt + 1))
    else
        break
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Infrastructure services failed to start within expected time"
    print_status "Checking service logs..."
    docker compose -f docker-compose.dev.yml logs
    exit 1
fi

print_success "Infrastructure services are ready"

# Build application services
print_status "Building application services..."
docker compose -f docker-compose.dev.yml build registry-service eligibility-service payment-service analytics-service

# Start application services
print_status "Starting application services..."
docker compose -f docker-compose.dev.yml up -d registry-service eligibility-service payment-service analytics-service

# Wait for application services to be ready
print_status "Waiting for application services to be ready..."
sleep 10

# Check service health
print_status "Checking service health..."
services=("registry-service:8001" "eligibility-service:8002" "payment-service:8003" "analytics-service:8004")
all_healthy=true

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        print_success "$service_name is healthy"
    else
        print_error "$service_name is not responding"
        all_healthy=false
    fi
done

if [ "$all_healthy" = false ]; then
    print_error "Some services are not healthy. Checking logs..."
    docker compose -f docker-compose.dev.yml logs --tail=50
    exit 1
fi

# Start dashboard if requested
if [ "${1:-}" = "--with-dashboard" ]; then
    print_status "Starting dashboard..."
    docker compose -f docker-compose.dev.yml up -d dashboard
    print_success "Dashboard started at http://localhost:3000"
fi

# Display deployment summary
echo ""
echo "🎉 DSRS Development Deployment Complete!"
echo "========================================"
echo ""
echo "📋 Service Status:"
echo "  • Registry Service:    http://localhost:8001"
echo "  • Eligibility Service: http://localhost:8002"
echo "  • Payment Service:     http://localhost:8003"
echo "  • Analytics Service:   http://localhost:8004"
echo ""
echo "🗄️  Infrastructure:"
echo "  • PostgreSQL:          localhost:5432 (user: dev, password: dev123)"
echo "  • Redpanda (Kafka):    localhost:9092"
echo "  • MongoDB:             localhost:27017 (user: dev, password: dev123)"
echo "  • Redis:               localhost:6379"
echo ""
echo "🔧 Management URLs:"
echo "  • Redpanda Console:    http://localhost:8082"
echo "  • Health Checks:       http://localhost:800[1-4]/health"
echo ""
if [ "${1:-}" = "--with-dashboard" ]; then
    echo "🌐 Dashboard:            http://localhost:3000"
    echo ""
fi
echo "📊 Quick Tests:"
echo "  curl http://localhost:8001/health"
echo "  curl http://localhost:8001/api/v1/households"
echo ""
echo "🛑 To stop all services:"
echo "  docker compose -f docker-compose.dev.yml down"
echo ""
echo "📝 To view logs:"
echo "  docker compose -f docker-compose.dev.yml logs -f [service-name]"
echo ""

# Run a quick smoke test
print_status "Running smoke tests..."
echo ""

# Test Registry Service
if curl -f -s "http://localhost:8001/api/v1/households" > /dev/null; then
    print_success "✅ Registry Service API is responding"
else
    print_warning "⚠️  Registry Service API test failed"
fi

# Test Analytics Service
if curl -f -s "http://localhost:8004/api/v1/metrics/summary" > /dev/null; then
    print_success "✅ Analytics Service API is responding"
else
    print_warning "⚠️  Analytics Service API test failed"
fi

echo ""
print_success "🚀 DSRS Development Environment is ready for use!"
echo ""
print_status "💡 Next steps:"
echo "   1. Run the test suite: ./scripts/run-tests.sh"
echo "   2. Create a test household: curl -X POST http://localhost:8001/api/v1/households -H 'Content-Type: application/json' -d '{...}'"
echo "   3. Check the analytics dashboard: http://localhost:8004/api/v1/metrics/summary"
echo ""
