#!/bin/bash

# Keycloak Configuration Script for DSRS
# This script configures Keycloak realm, clients, and roles for DSRS

set -euo pipefail

# Configuration
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD}"
REALM_NAME="dsrs"
CLIENT_ID="dsrs-web"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Wait for Keycloak to be ready
wait_for_keycloak() {
    log_info "Waiting for Keycloak to be ready..."
    
    timeout=300
    elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        if curl -f -s "$KEYCLOAK_URL/health/ready" > /dev/null 2>&1; then
            log_success "Keycloak is ready"
            return 0
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    log_error "Keycloak failed to become ready within $timeout seconds"
    return 1
}

# Get admin access token
get_admin_token() {
    log_info "Getting admin access token..."
    
    local response
    response=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$ADMIN_USER" \
        -d "password=$ADMIN_PASSWORD" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")
    
    if [[ $? -ne 0 ]]; then
        log_error "Failed to get admin token"
        return 1
    fi
    
    echo "$response" | jq -r '.access_token'
}

# Create DSRS realm
create_realm() {
    local token="$1"
    log_info "Creating DSRS realm..."
    
    local realm_config='{
        "realm": "'$REALM_NAME'",
        "enabled": true,
        "displayName": "Dynamic Social Registry System",
        "displayNameHtml": "<div class=\"kc-logo-text\"><span>Dynamic Social Registry System</span></div>",
        "loginTheme": "keycloak",
        "adminTheme": "keycloak",
        "accountTheme": "keycloak",
        "emailTheme": "keycloak",
        "sslRequired": "external",
        "registrationAllowed": false,
        "registrationEmailAsUsername": true,
        "rememberMe": true,
        "verifyEmail": false,
        "loginWithEmailAllowed": true,
        "duplicateEmailsAllowed": false,
        "resetPasswordAllowed": true,
        "editUsernameAllowed": false,
        "bruteForceProtected": true,
        "permanentLockout": false,
        "maxFailureWaitSeconds": 900,
        "minimumQuickLoginWaitSeconds": 60,
        "waitIncrementSeconds": 60,
        "quickLoginCheckMilliSeconds": 1000,
        "maxDeltaTimeSeconds": 43200,
        "failureFactor": 30,
        "defaultRoles": ["default-roles-'$REALM_NAME'"],
        "requiredCredentials": ["password"],
        "passwordPolicy": "length(8) and digits(1) and lowerCase(1) and upperCase(1) and specialChars(1) and notUsername",
        "otpPolicyType": "totp",
        "otpPolicyAlgorithm": "HmacSHA1",
        "otpPolicyInitialCounter": 0,
        "otpPolicyDigits": 6,
        "otpPolicyLookAheadWindow": 1,
        "otpPolicyPeriod": 30,
        "browserSecurityHeaders": {
            "contentSecurityPolicyReportOnly": "",
            "xContentTypeOptions": "nosniff",
            "xRobotsTag": "none",
            "xFrameOptions": "SAMEORIGIN",
            "contentSecurityPolicy": "frame-src '\''self'\''; frame-ancestors '\''self'\''; object-src '\''none'\'';"
        }
    }'
    
    local response
    response=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$realm_config")
    
    local http_code="${response: -3}"
    if [[ "$http_code" == "201" ]]; then
        log_success "DSRS realm created successfully"
    elif [[ "$http_code" == "409" ]]; then
        log_warning "DSRS realm already exists"
    else
        log_error "Failed to create DSRS realm (HTTP $http_code)"
        return 1
    fi
}

# Create client
create_client() {
    local token="$1"
    log_info "Creating DSRS client..."
    
    local client_config='{
        "clientId": "'$CLIENT_ID'",
        "name": "DSRS Web Application",
        "description": "Dynamic Social Registry System Web Application",
        "enabled": true,
        "clientAuthenticatorType": "client-secret",
        "secret": "'${KEYCLOAK_CLIENT_SECRET_STAGING}'",
        "redirectUris": [
            "https://staging.dsrs.gov.ph/api/auth/callback/keycloak",
            "http://localhost:3000/api/auth/callback/keycloak"
        ],
        "webOrigins": [
            "https://staging.dsrs.gov.ph",
            "http://localhost:3000"
        ],
        "protocol": "openid-connect",
        "publicClient": false,
        "bearerOnly": false,
        "consentRequired": false,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "directAccessGrantsEnabled": true,
        "serviceAccountsEnabled": false,
        "frontchannelLogout": true,
        "attributes": {
            "saml.assertion.signature": "false",
            "saml.force.post.binding": "false",
            "saml.multivalued.roles": "false",
            "saml.encrypt": "false",
            "saml.server.signature": "false",
            "saml.server.signature.keyinfo.ext": "false",
            "exclude.session.state.from.auth.response": "false",
            "saml_force_name_id_format": "false",
            "saml.client.signature": "false",
            "tls.client.certificate.bound.access.tokens": "false",
            "saml.authnstatement": "false",
            "display.on.consent.screen": "false",
            "saml.onetimeuse.condition": "false"
        },
        "fullScopeAllowed": true,
        "nodeReRegistrationTimeout": -1,
        "defaultClientScopes": [
            "web-origins",
            "role_list",
            "profile",
            "roles",
            "email"
        ],
        "optionalClientScopes": [
            "address",
            "phone",
            "offline_access",
            "microprofile-jwt"
        ]
    }'
    
    local response
    response=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/clients" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$client_config")
    
    local http_code="${response: -3}"
    if [[ "$http_code" == "201" ]]; then
        log_success "DSRS client created successfully"
    elif [[ "$http_code" == "409" ]]; then
        log_warning "DSRS client already exists"
    else
        log_error "Failed to create DSRS client (HTTP $http_code)"
        return 1
    fi
}

# Create roles
create_roles() {
    local token="$1"
    log_info "Creating DSRS roles..."
    
    local roles=(
        '{"name": "admin", "description": "Full system administrator access"}'
        '{"name": "operator", "description": "Standard operations access"}'
        '{"name": "quality", "description": "Quality assurance access"}'
        '{"name": "security", "description": "Security operations access"}'
        '{"name": "viewer", "description": "Read-only access"}'
        '{"name": "field-worker", "description": "Field operations access"}'
    )
    
    for role in "${roles[@]}"; do
        local role_name
        role_name=$(echo "$role" | jq -r '.name')
        
        local response
        response=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/roles" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$role")
        
        local http_code="${response: -3}"
        if [[ "$http_code" == "201" ]]; then
            log_success "Role '$role_name' created successfully"
        elif [[ "$http_code" == "409" ]]; then
            log_warning "Role '$role_name' already exists"
        else
            log_error "Failed to create role '$role_name' (HTTP $http_code)"
        fi
    done
}

# Create test users
create_test_users() {
    local token="$1"
    log_info "Creating test users..."
    
    local users=(
        '{"username": "admin-user", "email": "admin@dsrs.gov.ph", "firstName": "System", "lastName": "Administrator", "enabled": true, "emailVerified": true, "credentials": [{"type": "password", "value": "Admin123!", "temporary": false}], "realmRoles": ["admin"]}'
        '{"username": "operator-user", "email": "operator@dsrs.gov.ph", "firstName": "System", "lastName": "Operator", "enabled": true, "emailVerified": true, "credentials": [{"type": "password", "value": "Operator123!", "temporary": false}], "realmRoles": ["operator"]}'
        '{"username": "quality-user", "email": "quality@dsrs.gov.ph", "firstName": "Quality", "lastName": "Assurance", "enabled": true, "emailVerified": true, "credentials": [{"type": "password", "value": "Quality123!", "temporary": false}], "realmRoles": ["quality"]}'
        '{"username": "security-user", "email": "security@dsrs.gov.ph", "firstName": "Security", "lastName": "Officer", "enabled": true, "emailVerified": true, "credentials": [{"type": "password", "value": "Security123!", "temporary": false}], "realmRoles": ["security"]}'
        '{"username": "viewer-user", "email": "viewer@dsrs.gov.ph", "firstName": "System", "lastName": "Viewer", "enabled": true, "emailVerified": true, "credentials": [{"type": "password", "value": "Viewer123!", "temporary": false}], "realmRoles": ["viewer"]}'
    )
    
    for user in "${users[@]}"; do
        local username
        username=$(echo "$user" | jq -r '.username')
        
        local response
        response=$(curl -s -w "%{http_code}" -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$user")
        
        local http_code="${response: -3}"
        if [[ "$http_code" == "201" ]]; then
            log_success "User '$username' created successfully"
            
            # Get user ID and assign roles
            local user_id
            user_id=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users?username=$username" \
                -H "Authorization: Bearer $token" | jq -r '.[0].id')
            
            if [[ "$user_id" != "null" && "$user_id" != "" ]]; then
                # Get roles for this user
                local user_roles
                user_roles=$(echo "$user" | jq -r '.realmRoles[]')
                
                for role_name in $user_roles; do
                    # Get role representation
                    local role_rep
                    role_rep=$(curl -s -X GET "$KEYCLOAK_URL/admin/realms/$REALM_NAME/roles/$role_name" \
                        -H "Authorization: Bearer $token")
                    
                    # Assign role to user
                    curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users/$user_id/role-mappings/realm" \
                        -H "Authorization: Bearer $token" \
                        -H "Content-Type: application/json" \
                        -d "[$role_rep]"
                    
                    log_success "Assigned role '$role_name' to user '$username'"
                done
            fi
            
        elif [[ "$http_code" == "409" ]]; then
            log_warning "User '$username' already exists"
        else
            log_error "Failed to create user '$username' (HTTP $http_code)"
        fi
    done
}

# Get realm public key
get_realm_public_key() {
    local token="$1"
    log_info "Getting realm public key..."
    
    local realm_info
    realm_info=$(curl -s -X GET "$KEYCLOAK_URL/realms/$REALM_NAME" \
        -H "Authorization: Bearer $token")
    
    local public_key
    public_key=$(echo "$realm_info" | jq -r '.public_key')
    
    if [[ "$public_key" != "null" && "$public_key" != "" ]]; then
        log_success "Retrieved realm public key"
        echo "-----BEGIN PUBLIC KEY-----"
        echo "$public_key"
        echo "-----END PUBLIC KEY-----"
        
        # Save to file for Kong configuration
        {
            echo "-----BEGIN PUBLIC KEY-----"
            echo "$public_key"
            echo "-----END PUBLIC KEY-----"
        } > "$PROJECT_ROOT/secrets/keycloak-public-key.pem"
        
        log_success "Public key saved to secrets/keycloak-public-key.pem"
    else
        log_error "Failed to retrieve realm public key"
        return 1
    fi
}

# Main configuration function
main() {
    log_info "Starting Keycloak configuration for DSRS"
    echo "=========================================="
    
    # Wait for Keycloak to be ready
    wait_for_keycloak || exit 1
    
    # Get admin token
    local admin_token
    admin_token=$(get_admin_token) || exit 1
    
    if [[ -z "$admin_token" || "$admin_token" == "null" ]]; then
        log_error "Failed to get admin token"
        exit 1
    fi
    
    log_success "Admin token obtained"
    
    # Create realm
    create_realm "$admin_token" || exit 1
    
    # Create client
    create_client "$admin_token" || exit 1
    
    # Create roles
    create_roles "$admin_token" || exit 1
    
    # Create test users
    create_test_users "$admin_token" || exit 1
    
    # Get public key
    get_realm_public_key "$admin_token" || exit 1
    
    log_success "Keycloak configuration completed successfully!"
    
    echo ""
    echo "Configuration Summary:"
    echo "====================="
    echo "Realm: $REALM_NAME"
    echo "Client ID: $CLIENT_ID"
    echo "Keycloak URL: $KEYCLOAK_URL"
    echo ""
    echo "Test Users Created:"
    echo "- admin-user / Admin123!"
    echo "- operator-user / Operator123!"
    echo "- quality-user / Quality123!"
    echo "- security-user / Security123!"
    echo "- viewer-user / Viewer123!"
    echo ""
    echo "Next Steps:"
    echo "1. Update Kong configuration with the public key"
    echo "2. Test authentication flow"
    echo "3. Configure additional users as needed"
}

# Run main function
main "$@"
