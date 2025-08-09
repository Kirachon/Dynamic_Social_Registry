# DSRS Implementation Audit Report

This report identifies gaps between the Dynamic Social Registry System (DSRS) Single Source of Truth and the current implementation. It focuses on APIs/services, security, data models, eventing, Kubernetes/infra, observability, and testing. Each gap is labeled with a suggested priority.

## 1) Unimplemented Features

- Core microservices (documented, not present)
  - Workflow, Document, Notification, Audit, Reporting services
  - Partner integrations (PhilSys, LandBank/GCash/PayMaya, DepEd/DOH/DOLE) and adapters
  - Mobile apps (React Native/Flutter) and USSD/SMS channels
  - Service Mesh (Istio) with mTLS, retries, timeouts, canary/blue-green
  - Search stack (Elasticsearch, Logstash, Kibana) and indexing pipelines
  - Data Lake/Warehouse and ETL pipelines (BigQuery, Dataflow)
  - Priority: Critical for core services/security; High for ops/integrations

- Security features (documented, not present)
  - Zero Trust continuous auth, device/location checks
  - MFA (OTP/SMS/Biometrics), RBAC/ABAC, centralized policy
  - KMS-based encryption-at-rest and column-level encryption for sensitive data
  - DLP (e.g., Google Cloud DLP) and periodic privacy audits; SIEM/SOC pipelines
  - Priority: Critical

- API/Domain functionality
  - Rich Registry CRUD and search (filtering, pagination, indexing)
  - Program enrollment, case management workflows
  - Identity verification with external IdP and national ID system (PhilSys flows)
  - Notification delivery (SMS/Email), document management, admin/reporting endpoints
  - Priority: High

- Deployment/Operations
  - Terraform/IaC and Helm charts; DR/BCP specifics and runbooks
  - SLO dashboards and alerting (Prometheus/Grafana)
  - Priority: High

## 2) Partially Implemented Components

- API Gateway and Auth
  - Kong deployed with CORS, rate limiting and basic JWT claim checks.
  - OIDC/JWKS verification at the gateway not configured; backend services allow dev bypass.
  - Priority: Critical (OIDC at edge), High (turn off bypass outside dev)

- Registry service
  - Implemented endpoints: GET list, GET summary, POST create, PUT update.
  - Saga emission: `registry.household.registered` on create/update.
  - Gap: Outbox event insert not atomic with business write (separate DB session).

```python
# Current (non-atomic)
# services/registry/app/main.py
...
db.commit()
emit_household_registered(h)  # outbox in a new session, risk of lost event
```

  - Priority: Critical

- Eligibility service
  - Consumes `registry.household`; simple rule (approved if pmt_score <= 0.3).
  - Writes decision; emits `eligibility.assessed.*` via outbox; idempotency present; DLQ publish present.
  - Missing: DLQ re-processing worker (retries/backoff); richer decision rationale.
  - Priority: High

- Payment service
  - Consumes `eligibility.assessed.approved`; creates Scheduled payment; emits `payment.scheduled`; completer emits `payment.completed`.
  - Idempotency present; DLQ publish present; no DLQ reprocessor.
  - Priority: High

- Analytics service
  - Consumes eligibility and payment events; maintains counters in Mongo.
  - Public `/api/v1/analytics/summary` returns static values (not wired to counters).
  - Priority: Medium

- Eventing & Observability
  - Redpanda/Strimzi and topics present; transactional outbox present; OTEL produce/consume spans and header propagation implemented; Prometheus counters present.
  - Missing: Prometheus/OTEL Collector deployments; histograms/timers; dashboards/alerts.
  - Priority: High

- Testing
  - Unit tests minimal; e2e saga test present (bounded) but relies on in-process apps; background worker startup may be flaky without lifespan management.
  - Priority: High

## 3) Missing Infrastructure

- Kubernetes
  - Partial manifests (Kong, Strimzi, some Deployments). Missing full overlays for all services, TLS/Ingress, External Secrets, NetworkPolicies, HPAs, PDBs, PodSecurity.
  - Service Mesh (Istio) absent.
  - Priority: Critical (TLS/Ingress/Secrets), High (mesh, policies, autoscaling)

- CI/CD
  - No image build/publish, Helm/Terraform deploy pipelines.
  - Priority: High

- Observability stack
  - No Prometheus/Grafana or OTEL Collector manifests; no centralized logs (ELK) or SIEM streaming.
  - Priority: High

- Secrets/config
  - Plain env vars; no external secret manager integration; no rotation.
  - Priority: Critical

## 4) Technical Debt

- Transactional Outbox atomicity (Registry)
  - Business write commits, then outbox insert — risks lost events on failure.
  - Fix: Insert outbox in the same DB transaction/session before commit; or DB trigger-based outbox.
  - Priority: Critical

- DLQ strategy
  - DLQ publish exists; no reprocessor/retry/backoff; no visibility.
  - Fix: DLQ worker that re-publishes after backoff with max retries; counters and alerts.
  - Priority: High

- Trace & metrics consistency
  - Add explicit processing spans; extend metrics to histograms; deploy OTEL Collector and Prometheus.
  - Priority: High

- Security posture
  - Configure Kong OIDC w/ Keycloak; disable dev bypass in non-dev; add RBAC/ABAC; per-route rate limiting; mTLS (mesh).
  - Priority: Critical

- Test robustness
  - Ensure background workers start/stop deterministically in tests (lifespan or separate processes/containers).
  - Priority: High

- Schema/domain depth
  - Add indexes, constraints, audit fields; expand domain endpoints and validation.
  - Priority: Medium

## 5) Priority Assessment (Backlog)

- Critical
  - Kong OIDC/JWKS; remove insecure bypass outside dev; TLS ingress
  - Atomic outbox for Registry POST/PUT
  - K8s prod readiness: Secrets/Ingress/NetworkPolicy/health checks

- High
  - DLQ reprocessor with retry/backoff; Prometheus + OTEL Collector deployments
  - Robust e2e tests (lifespan-managed); dashboards/alerts

- Medium
  - Analytics endpoints wired to Mongo counters; schema/enrichment
  - Helm/Terraform; CI pipelines for images/deploy

- Low
  - Additional microservices scaffolds; external integration stubs
  - Service mesh (Istio) and ELK after core hardening

## 6) Recommendations (Phase 1)

- Security: Configure Kong OIDC/JWKS with Keycloak; disable ALLOW_INSECURE_LOCAL in non-dev; enforce TLS via Ingress.
- Reliability: Ensure outbox inserts occur in the same transaction as household writes in Registry.
- Observability: Add OTEL Collector and Prometheus to docker-compose and K8s; wire scrape/export; minimal dashboards.
- Messaging Resilience: Implement DLQ reprocessor with retry/backoff and tests.

