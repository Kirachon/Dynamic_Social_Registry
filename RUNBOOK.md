# DSRS Operations Runbook

## Overview
This runbook provides step-by-step procedures for common operational tasks in the Dynamic Social Registry System (DSRS). All procedures use only open-source tools and technologies.

## 🚀 **Deployment Procedures**

### **Standard Deployment**
```bash
# 1. Pre-deployment checks
./scripts/pre-deployment-check.sh

# 2. Backup current system
./scripts/backup-system.sh

# 3. Deploy new version
./scripts/deploy-staging.sh

# 4. Post-deployment verification
./scripts/post-deployment-check.sh

# 5. Update monitoring dashboards
./scripts/update-monitoring.sh
```

### **Emergency Rollback**
```bash
# 1. Stop current services
docker-compose down

# 2. Restore from backup
./scripts/restore-backup.sh [backup-timestamp]

# 3. Start previous version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify system health
./scripts/health-check.sh

# 5. Notify stakeholders
./scripts/send-notification.sh "System rolled back to previous version"
```

## 🔧 **Service Management**

### **Start All Services**
```bash
# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Staging environment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Verify all services are running
docker-compose ps
```

### **Stop All Services**
```bash
# Graceful shutdown
docker-compose down

# Force stop if needed
docker-compose down --timeout 30

# Remove volumes (CAUTION: Data loss)
docker-compose down -v
```

### **Restart Individual Service**
```bash
# Restart specific service
docker-compose restart [service-name]

# Examples
docker-compose restart registry
docker-compose restart kong
docker-compose restart keycloak

# Check service logs
docker-compose logs -f [service-name]
```

### **Scale Services**
```bash
# Scale microservices
docker-compose up -d --scale registry=3
docker-compose up -d --scale eligibility=2
docker-compose up -d --scale payment=2

# Verify scaling
docker-compose ps
```

## 🗄️ **Database Operations**

### **PostgreSQL Management**
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U dsrs_user -d dsrs

# Create database backup
docker-compose exec postgres pg_dump -U dsrs_user dsrs > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T postgres psql -U dsrs_user -d dsrs < backup_file.sql

# Check database connections
docker-compose exec postgres psql -U dsrs_user -d dsrs -c "SELECT count(*) FROM pg_stat_activity;"

# Run database migrations
docker-compose exec registry alembic upgrade head
docker-compose exec eligibility alembic upgrade head
docker-compose exec payment alembic upgrade head
```

### **MongoDB Management**
```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh dsrs

# Create MongoDB backup
docker-compose exec mongodb mongodump --db dsrs --out /backup/mongodb_$(date +%Y%m%d_%H%M%S)

# Restore MongoDB
docker-compose exec mongodb mongorestore --db dsrs /backup/mongodb_backup_folder

# Check MongoDB status
docker-compose exec mongodb mongosh --eval "db.adminCommand('serverStatus')"

# Monitor collections
docker-compose exec mongodb mongosh dsrs --eval "db.stats()"
```

## 📊 **Monitoring & Alerting**

### **Check System Health**
```bash
# Overall system health
curl -f http://localhost:8001/status  # Kong health
curl -f http://localhost:8080/health/ready  # Keycloak health
curl -f http://localhost:3000/api/health  # Frontend health

# Individual service health
curl -f http://localhost:8000/registry/health
curl -f http://localhost:8000/eligibility/health
curl -f http://localhost:8000/payment/health
curl -f http://localhost:8000/analytics/health

# Database connectivity
docker-compose exec postgres pg_isready -U dsrs_user -d dsrs
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### **View Service Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f registry
docker-compose logs -f kong
docker-compose logs -f keycloak

# Filter logs by time
docker-compose logs --since="1h" registry
docker-compose logs --tail=100 eligibility

# Search logs
docker-compose logs registry | grep ERROR
docker-compose logs kong | grep "HTTP/1.1\" 5"
```

### **Monitor Resource Usage**
```bash
# Container resource usage
docker stats

# System resource usage
htop
df -h
free -h

# Network connections
netstat -tulpn
ss -tulpn

# Disk I/O
iostat -x 1
```

## 🔐 **Security Operations**

### **Certificate Management**
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/dsrs.crt -text -noout | grep "Not After"

# Renew Let's Encrypt certificates
certbot renew --dry-run
certbot renew

# Restart services after certificate renewal
docker-compose restart kong
docker-compose restart web
```

### **User Management (Keycloak)**
```bash
# Access Keycloak admin console
# URL: https://auth.yourdomain.com
# Username: admin
# Password: [from environment]

# Reset user password via CLI
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 --realm master --user admin --password $KEYCLOAK_ADMIN_PASSWORD

docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh set-password \
  --realm dsrs --username [username] --new-password [new-password]

# List users
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh get users --realm dsrs

# Disable user
docker-compose exec keycloak /opt/keycloak/bin/kcadm.sh update users/[user-id] \
  --realm dsrs --set enabled=false
```

### **Security Monitoring**
```bash
# Check failed login attempts
docker-compose logs keycloak | grep "LOGIN_ERROR"

# Monitor API rate limiting
docker-compose logs kong | grep "rate-limiting"

# Check for suspicious activity
docker-compose logs kong | grep "4[0-9][0-9]\|5[0-9][0-9]"

# Review audit logs
docker-compose logs registry | grep "audit"
docker-compose logs eligibility | grep "audit"
```

## 🔄 **Backup & Recovery**

### **Create System Backup**
```bash
#!/bin/bash
# Full system backup script

BACKUP_DIR="/backup/dsrs_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Database backups
docker-compose exec postgres pg_dump -U dsrs_user dsrs > $BACKUP_DIR/postgres_dsrs.sql
docker-compose exec postgres pg_dump -U kong kong > $BACKUP_DIR/postgres_kong.sql
docker-compose exec postgres pg_dump -U keycloak keycloak > $BACKUP_DIR/postgres_keycloak.sql
docker-compose exec mongodb mongodump --db dsrs --out $BACKUP_DIR/mongodb

# Configuration backups
cp -r .env* $BACKUP_DIR/
cp -r infra/ $BACKUP_DIR/
cp -r scripts/ $BACKUP_DIR/
cp docker-compose*.yml $BACKUP_DIR/

# Create archive
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup created: $BACKUP_DIR.tar.gz"
```

### **Restore System from Backup**
```bash
#!/bin/bash
# System restore script

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    exit 1
fi

# Extract backup
tar -xzf $BACKUP_FILE
BACKUP_DIR=$(basename $BACKUP_FILE .tar.gz)

# Stop services
docker-compose down

# Restore databases
docker-compose up -d postgres mongodb
sleep 30

docker-compose exec -T postgres psql -U dsrs_user -d dsrs < $BACKUP_DIR/postgres_dsrs.sql
docker-compose exec -T postgres psql -U kong -d kong < $BACKUP_DIR/postgres_kong.sql
docker-compose exec -T postgres psql -U keycloak -d keycloak < $BACKUP_DIR/postgres_keycloak.sql
docker-compose exec mongodb mongorestore --db dsrs $BACKUP_DIR/mongodb/dsrs

# Restore configuration
cp $BACKUP_DIR/.env* ./
cp -r $BACKUP_DIR/infra/ ./
cp -r $BACKUP_DIR/scripts/ ./
cp $BACKUP_DIR/docker-compose*.yml ./

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "System restored from backup: $BACKUP_FILE"
```

## 🚨 **Incident Response**

### **Service Down**
1. **Identify affected service**
   ```bash
   docker-compose ps
   curl -f http://localhost:8000/[service]/health
   ```

2. **Check service logs**
   ```bash
   docker-compose logs --tail=100 [service]
   ```

3. **Restart service**
   ```bash
   docker-compose restart [service]
   ```

4. **Verify recovery**
   ```bash
   curl -f http://localhost:8000/[service]/health
   ```

5. **Notify stakeholders**
   ```bash
   ./scripts/send-notification.sh "Service [service] recovered"
   ```

### **Database Connection Issues**
1. **Check database status**
   ```bash
   docker-compose exec postgres pg_isready -U dsrs_user -d dsrs
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
   ```

2. **Check connection pools**
   ```bash
   docker-compose exec postgres psql -U dsrs_user -d dsrs -c "SELECT count(*) FROM pg_stat_activity;"
   ```

3. **Restart database if needed**
   ```bash
   docker-compose restart postgres
   docker-compose restart mongodb
   ```

4. **Restart dependent services**
   ```bash
   docker-compose restart registry eligibility payment analytics
   ```

### **High Resource Usage**
1. **Identify resource bottleneck**
   ```bash
   docker stats
   htop
   df -h
   ```

2. **Scale services if needed**
   ```bash
   docker-compose up -d --scale registry=3
   docker-compose up -d --scale eligibility=2
   ```

3. **Clean up logs and temporary files**
   ```bash
   docker system prune -f
   docker volume prune -f
   journalctl --vacuum-time=7d
   ```

4. **Monitor improvement**
   ```bash
   watch docker stats
   ```

## 📈 **Performance Tuning**

### **Database Optimization**
```bash
# PostgreSQL performance tuning
docker-compose exec postgres psql -U dsrs_user -d dsrs -c "
ANALYZE;
REINDEX DATABASE dsrs;
VACUUM ANALYZE;
"

# MongoDB performance tuning
docker-compose exec mongodb mongosh dsrs --eval "
db.runCommand({compact: 'households'});
db.runCommand({reIndex: 'households'});
"

# Check slow queries
docker-compose exec postgres psql -U dsrs_user -d dsrs -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### **Application Performance**
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/registry/api/v1/households

# Monitor Kafka consumer lag
docker-compose exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --describe --all-groups

# Clear application caches
docker-compose restart redis  # if using Redis
docker-compose exec web npm run cache:clear  # if applicable
```

## 🔍 **Troubleshooting Guide**

### **Common Issues**

#### **Kong JWT Verification Fails**
```bash
# Check Keycloak public key
curl -s http://localhost:8080/realms/dsrs | jq -r '.public_key'

# Update Kong JWT configuration
# Edit infra/kong/kong.yml with correct public key
docker-compose restart kong
```

#### **Frontend Authentication Issues**
```bash
# Check NextAuth configuration
docker-compose logs web | grep "nextauth"

# Verify Keycloak client configuration
# Check redirect URIs and client secret

# Clear browser cookies and try again
```

#### **Database Migration Errors**
```bash
# Check migration status
docker-compose exec registry alembic current
docker-compose exec registry alembic history

# Manually run specific migration
docker-compose exec registry alembic upgrade [revision]

# Rollback migration if needed
docker-compose exec registry alembic downgrade [revision]
```

#### **Kafka Consumer Lag**
```bash
# Check consumer group status
docker-compose exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --describe --group [group-name]

# Reset consumer offset if needed
docker-compose exec kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --group [group-name] --reset-offsets --to-latest --all-topics --execute

# Restart consumer services
docker-compose restart eligibility payment analytics
```

## 📞 **Emergency Contacts**

### **Technical Team**
- **System Administrator**: admin@dsrs.gov.ph
- **Database Administrator**: dba@dsrs.gov.ph
- **Security Team**: security@dsrs.gov.ph
- **Development Team**: dev@dsrs.gov.ph

### **Business Contacts**
- **Project Manager**: pm@dsrs.gov.ph
- **Business Owner**: owner@dsrs.gov.ph
- **End User Support**: support@dsrs.gov.ph

### **External Vendors**
- **Hosting Provider**: [Provider contact information]
- **Domain Registrar**: [Registrar contact information]
- **SSL Certificate Provider**: [Certificate provider contact]

## 📋 **Maintenance Schedule**

### **Daily Tasks**
- Monitor system health and performance
- Review error logs and alerts
- Check backup completion status
- Verify SSL certificate validity

### **Weekly Tasks**
- Review security logs and access patterns
- Update system packages and security patches
- Clean up old logs and temporary files
- Test backup and restore procedures

### **Monthly Tasks**
- Review and update documentation
- Conduct security vulnerability scans
- Analyze performance trends and capacity planning
- Review and update monitoring thresholds

### **Quarterly Tasks**
- Conduct disaster recovery testing
- Review and update incident response procedures
- Security audit and penetration testing
- Performance optimization and tuning

---

This runbook provides comprehensive operational procedures for the DSRS system using only open-source tools and technologies. Regular updates to this document should be made as the system evolves and new procedures are developed.
