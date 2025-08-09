# DSRS Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Dynamic Social Registry System (DSRS) to staging and production environments using only open-source technologies.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Frontend      │    │   Kong API   │    │  Microservices  │
│   (Next.js)     │───▶│   Gateway    │───▶│   (FastAPI)     │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                       │
                              ▼                       ▼
                    ┌──────────────┐         ┌─────────────────┐
                    │   Keycloak   │         │   Databases     │
                    │    (OSS)     │         │ (PostgreSQL,    │
                    └──────────────┘         │  MongoDB)       │
                                            └─────────────────┘
```

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended for production)
- **Storage**: 50GB+ SSD
- **Network**: Public IP with ports 80, 443, 8080 accessible

### Software Dependencies
- Docker 24.0+
- Docker Compose 2.0+
- Git
- OpenSSL (for certificate generation)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/Kirachon/Dynamic_Social_Registry.git
cd Dynamic_Social_Registry
git checkout implementation
```

### 2. Create Environment Files

#### Backend Services (.env)
```bash
# Copy template
cp .env.example .env

# Edit with production values
nano .env
```

Required environment variables:
```env
# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=dsrs
POSTGRES_USER=dsrs_user
POSTGRES_PASSWORD=<secure-password>

# MongoDB Configuration
MONGODB_URL=mongodb://mongo_user:<secure-password>@mongodb:27017/dsrs

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_PREFIX=dsrs

# Kong Configuration
KONG_DATABASE=postgres
KONG_PG_HOST=postgres
KONG_PG_USER=kong
KONG_PG_PASSWORD=<secure-password>
KONG_PG_DATABASE=kong

# Security
JWT_SECRET=<generate-secure-secret>
CORS_ALLOW_ORIGINS=https://your-domain.com

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=<secure-password>
```

#### Frontend (.env.local)
```bash
cd web
cp .env.local.example .env.local
nano .env.local
```

```env
# API Configuration
NEXT_PUBLIC_API_BASE=https://api.your-domain.com

# NextAuth Configuration
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=<generate-secure-secret>

# Keycloak Configuration
KEYCLOAK_ISSUER=https://auth.your-domain.com/realms/dsrs
KEYCLOAK_CLIENT_ID=dsrs-web
KEYCLOAK_CLIENT_SECRET=<keycloak-client-secret>

# Production Settings
NODE_ENV=production
NEXT_PUBLIC_DEV_MODE=0
```

## Keycloak Configuration

### 1. Initial Setup
```bash
# Start Keycloak
docker compose up -d keycloak

# Access admin console
# URL: http://localhost:8080
# Username: admin
# Password: admin (change immediately)
```

### 2. Create DSRS Realm
1. Login to Keycloak Admin Console
2. Click "Add Realm"
3. Name: `dsrs`
4. Click "Create"

### 3. Create Client
1. Navigate to Clients → Create
2. Client ID: `dsrs-web`
3. Client Protocol: `openid-connect`
4. Access Type: `confidential`
5. Valid Redirect URIs: `https://your-domain.com/api/auth/callback/keycloak`
6. Web Origins: `https://your-domain.com`
7. Save and note the Client Secret

### 4. Create Roles
Navigate to Roles → Add Role:
- `admin` - Full system access
- `operator` - Standard operations access
- `quality` - Quality assurance access
- `security` - Security operations access
- `viewer` - Read-only access

### 5. Create Test Users
1. Navigate to Users → Add User
2. Username: `admin-user`
3. Email: `admin@your-domain.com`
4. Set password in Credentials tab
5. Assign roles in Role Mappings tab

## Kong API Gateway Configuration

### 1. Database Setup
Kong requires PostgreSQL. This is handled in docker-compose.yml.

### 2. Kong Configuration
```yaml
# kong.yml (declarative config)
_format_version: "3.0"
_transform: true

services:
  - name: identity
    url: http://identity:8000
    routes:
      - name: identity-route
        paths: ["/identity"]
        strip_path: true
  - name: registry
    url: http://registry:8000
    routes:
      - name: registry-route
        paths: ["/registry"]
        strip_path: true
  - name: eligibility
    url: http://eligibility:8000
    routes:
      - name: eligibility-route
        paths: ["/eligibility"]
        strip_path: true
  - name: payment
    url: http://payment:8000
    routes:
      - name: payment-route
        paths: ["/payment"]
        strip_path: true
  - name: analytics
    url: http://analytics:8000
    routes:
      - name: analytics-route
        paths: ["/analytics"]
        strip_path: true

plugins:
  - name: cors
    config:
      origins: ["https://your-domain.com"]
      methods: ["GET","POST","PUT","DELETE","OPTIONS"]
      headers: ["Authorization","Content-Type"]
      credentials: true
  - name: rate-limiting
    config:
      minute: 1000
      policy: local
  - name: jwt
    config:
      uri_param_names: ["jwt"]
      cookie_names: ["dsrs_token"]
      claims_to_verify: ["exp"]
      key_claim_name: iss
      secret_is_base64: false

consumers:
  - username: keycloak
    jwt_secrets:
      - key: "https://auth.your-domain.com/realms/dsrs"
        secret: "-----BEGIN PUBLIC KEY-----\n<keycloak-public-key>\n-----END PUBLIC KEY-----"
```

### 3. Get Keycloak Public Key
```bash
curl https://auth.your-domain.com/realms/dsrs | jq -r '.public_key'
```

## Database Migration

### 1. PostgreSQL Setup
```bash
# Create databases
docker compose exec postgres psql -U postgres -c "CREATE DATABASE dsrs;"
docker compose exec postgres psql -U postgres -c "CREATE DATABASE kong;"
docker compose exec postgres psql -U postgres -c "CREATE USER dsrs_user WITH PASSWORD 'secure-password';"
docker compose exec postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE dsrs TO dsrs_user;"
```

### 2. Run Migrations
```bash
# Registry service
docker compose exec registry alembic upgrade head

# Eligibility service
docker compose exec eligibility alembic upgrade head

# Payment service
docker compose exec payment alembic upgrade head
```

### 3. MongoDB Setup
```bash
# Create MongoDB user
docker compose exec mongodb mongo admin --eval "
db.createUser({
  user: 'mongo_user',
  pwd: 'secure-password',
  roles: [{role: 'readWrite', db: 'dsrs'}]
})
"
```

## SSL/TLS Configuration

### 1. Generate Certificates (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com -d api.your-domain.com -d auth.your-domain.com

# Certificates will be in /etc/letsencrypt/live/your-domain.com/
```

### 2. Configure Nginx (Reverse Proxy)
```nginx
# /etc/nginx/sites-available/dsrs
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name auth.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com api.your-domain.com auth.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Deployment Steps

### 1. Staging Deployment
```bash
# 1. Prepare environment
export ENVIRONMENT=staging
export DOMAIN=staging.your-domain.com

# 2. Build and start services
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# 3. Wait for services to be ready
./scripts/wait-for-services.sh

# 4. Run database migrations
./scripts/migrate-databases.sh

# 5. Configure Kong
./scripts/configure-kong.sh

# 6. Setup Keycloak
./scripts/setup-keycloak.sh

# 7. Build and deploy frontend
cd web
npm ci
npm run build
npm start &

# 8. Run health checks
./scripts/health-check.sh
```

### 2. Production Deployment
```bash
# 1. Prepare production environment
export ENVIRONMENT=production
export DOMAIN=your-domain.com

# 2. Deploy with production compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Follow same steps as staging with production configs
```

## Monitoring and Observability

### 1. Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dsrs-services'
    static_configs:
      - targets: ['registry:8000', 'eligibility:8000', 'payment:8000', 'analytics:8000']
    metrics_path: /metrics
    
  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: /metrics
```

### 2. Grafana Dashboards
Import pre-configured dashboards from `monitoring/grafana/dashboards/`

### 3. Alerting Rules
```yaml
# alerts.yml
groups:
  - name: dsrs-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
```

## Security Considerations

### 1. Network Security
- Use firewall to restrict access to necessary ports only
- Implement VPN for administrative access
- Use private networks for inter-service communication

### 2. Secrets Management
- Use Docker secrets or external secret management
- Rotate passwords regularly
- Use strong, unique passwords for all services

### 3. Regular Updates
- Keep all Docker images updated
- Monitor security advisories for dependencies
- Implement automated security scanning

## Backup and Recovery

### 1. Database Backups
```bash
# PostgreSQL backup
docker compose exec postgres pg_dump -U dsrs_user dsrs > backup_$(date +%Y%m%d).sql

# MongoDB backup
docker compose exec mongodb mongodump --db dsrs --out /backup/
```

### 2. Configuration Backups
```bash
# Backup all configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env web/.env.local kong.yml keycloak/ monitoring/
```

### 3. Recovery Procedures
Document step-by-step recovery procedures for:
- Database restoration
- Service configuration restoration
- Complete system recovery

## Troubleshooting

### Common Issues

1. **Kong JWT Verification Fails**
   - Verify Keycloak public key in Kong configuration
   - Check JWT token format and claims
   - Ensure clock synchronization between services

2. **Database Connection Issues**
   - Check database credentials
   - Verify network connectivity
   - Check database service health

3. **Frontend Authentication Issues**
   - Verify Keycloak client configuration
   - Check NextAuth.js configuration
   - Ensure proper redirect URIs

### Log Analysis
```bash
# View service logs
docker compose logs -f <service-name>

# View Kong logs
docker compose logs -f kong

# View Keycloak logs
docker compose logs -f keycloak
```

## Performance Tuning

### 1. Database Optimization
- Configure PostgreSQL connection pooling
- Optimize MongoDB indexes
- Monitor query performance

### 2. Application Tuning
- Configure appropriate worker processes
- Implement caching strategies
- Optimize API response times

### 3. Infrastructure Scaling
- Use load balancers for high availability
- Implement horizontal scaling for stateless services
- Monitor resource utilization

## Maintenance

### 1. Regular Tasks
- Monitor system health and performance
- Review and rotate logs
- Update security patches
- Backup verification

### 2. Scheduled Maintenance
- Database maintenance and optimization
- Certificate renewal
- Dependency updates
- Performance reviews

This deployment guide provides a comprehensive foundation for deploying DSRS in production environments while maintaining security, scalability, and reliability standards.
