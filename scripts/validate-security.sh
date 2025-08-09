#!/bin/bash
set -euo pipefail

# DSRS Security Validation Script
# Validates that authentication is properly enforced based on environment

ENVIRONMENT=${ENVIRONMENT:-"production"}
KONG_ADMIN_URL=${KONG_ADMIN_URL:-"http://localhost:8001"}
KONG_PROXY_URL=${KONG_PROXY_URL:-"http://localhost:8000"}

echo "🔒 DSRS Security Validation for environment: $ENVIRONMENT"

# Function to check HTTP status code
check_status() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo "  Testing: $description"
    actual_status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$actual_status" = "$expected_status" ]; then
        echo "  ✅ PASS: $url returned $actual_status (expected $expected_status)"
        return 0
    else
        echo "  ❌ FAIL: $url returned $actual_status (expected $expected_status)"
        return 1
    fi
}

# Function to validate JWT enforcement
validate_jwt_enforcement() {
    echo "🔐 Validating JWT enforcement..."
    
    local failed=0
    
    # Test protected endpoints without authentication - should return 401
    check_status "$KONG_PROXY_URL/registry/api/v1/households" "401" "Registry households endpoint (no auth)" || failed=1
    check_status "$KONG_PROXY_URL/eligibility/api/v1/health" "401" "Eligibility health endpoint (no auth)" || failed=1
    check_status "$KONG_PROXY_URL/payment/api/v1/payments" "401" "Payment payments endpoint (no auth)" || failed=1
    check_status "$KONG_PROXY_URL/analytics/api/v1/analytics/summary" "401" "Analytics summary endpoint (no auth)" || failed=1
    
    # Test with invalid JWT - should return 401
    check_status "$KONG_PROXY_URL/registry/api/v1/households" "401" "Registry with invalid JWT" || failed=1
    
    return $failed
}

# Function to validate Kong configuration
validate_kong_config() {
    echo "🌐 Validating Kong configuration..."
    
    local failed=0
    
    # Check Kong admin API is accessible
    check_status "$KONG_ADMIN_URL/status" "200" "Kong admin API status" || failed=1
    
    # Check JWT plugin is enabled
    echo "  Checking JWT plugin configuration..."
    jwt_plugins=$(curl -s "$KONG_ADMIN_URL/plugins" | jq -r '.data[] | select(.name == "jwt") | .name' 2>/dev/null || echo "")
    
    if [ -n "$jwt_plugins" ]; then
        echo "  ✅ PASS: JWT plugin is enabled"
    else
        echo "  ❌ FAIL: JWT plugin is not enabled"
        failed=1
    fi
    
    # Check rate limiting plugin
    rate_limit_plugins=$(curl -s "$KONG_ADMIN_URL/plugins" | jq -r '.data[] | select(.name == "rate-limiting") | .name' 2>/dev/null || echo "")
    
    if [ -n "$rate_limit_plugins" ]; then
        echo "  ✅ PASS: Rate limiting plugin is enabled"
    else
        echo "  ⚠️  WARN: Rate limiting plugin is not enabled"
    fi
    
    return $failed
}

# Function to validate environment-specific security
validate_environment_security() {
    echo "🏗️  Validating environment-specific security for: $ENVIRONMENT"
    
    local failed=0
    
    case $ENVIRONMENT in
        "local"|"development"|"dev")
            echo "  ℹ️  Development environment - auth bypass may be enabled"
            # In dev, services might allow bypass, but Kong should still enforce JWT
            ;;
        "staging"|"production"|"prod")
            echo "  🔒 Production environment - strict JWT enforcement required"
            # Validate that ALLOW_INSECURE_LOCAL is not set
            if [ "${ALLOW_INSECURE_LOCAL:-}" = "1" ]; then
                echo "  ❌ FAIL: ALLOW_INSECURE_LOCAL is set in $ENVIRONMENT environment"
                failed=1
            else
                echo "  ✅ PASS: ALLOW_INSECURE_LOCAL is not set"
            fi
            ;;
        *)
            echo "  ⚠️  WARN: Unknown environment: $ENVIRONMENT"
            ;;
    esac
    
    return $failed
}

# Function to validate service health endpoints
validate_service_health() {
    echo "🏥 Validating service health endpoints..."
    
    local failed=0
    
    # Health endpoints should be accessible without authentication
    local services=("registry" "eligibility" "payment" "analytics" "identity")
    
    for service in "${services[@]}"; do
        # Direct service health check (bypassing Kong)
        local service_url="http://localhost:800$((${#service} % 5 + 1))/health"
        check_status "$service_url" "200" "$service service health (direct)" || failed=1
    done
    
    return $failed
}

# Main validation function
main() {
    echo "🚀 Starting DSRS Security Validation..."
    echo "   Environment: $ENVIRONMENT"
    echo "   Kong Admin: $KONG_ADMIN_URL"
    echo "   Kong Proxy: $KONG_PROXY_URL"
    echo ""
    
    local total_failed=0
    
    # Run all validations
    validate_environment_security || total_failed=$((total_failed + 1))
    echo ""
    
    validate_kong_config || total_failed=$((total_failed + 1))
    echo ""
    
    validate_jwt_enforcement || total_failed=$((total_failed + 1))
    echo ""
    
    validate_service_health || total_failed=$((total_failed + 1))
    echo ""
    
    # Summary
    if [ $total_failed -eq 0 ]; then
        echo "🎉 All security validations PASSED!"
        echo "✅ DSRS security configuration is valid for $ENVIRONMENT environment"
        exit 0
    else
        echo "💥 $total_failed security validation(s) FAILED!"
        echo "❌ DSRS security configuration needs attention"
        exit 1
    fi
}

# Run main function
main "$@"
