# DSRS Codebase Audit

This audit compiles the current implementation status of the Dynamic Social Registry System (DSRS), assesses technical debt, and proposes a prioritized roadmap for the next iterations. It reflects the latest integration verification where the end‑to‑end choreography saga (Registry → Eligibility → Payment → Analytics) was validated locally with Kafka, Postgres, and MongoDB.

## Executive Summary
- Overall completion (feature + infra readiness): ~70%
- End‑to‑end saga flow: Working (local/dev), with transactional outbox and idempotent consumers
- Observability: Foundations in place (OTEL + Prometheus + Grafana + service health probes), dashboards/alerts need hardening
- Security: Development-only auth bypass present; production-grade edge auth (Kong/OIDC/JWT) needs completion
- Testing: CI present; unit/e2e coverage needs to grow; reliability tests and DLQ reprocessing tests pending

Key gaps to production:
- Enforce authentication/authorization at the gateway and services (disable dev bypass outside local)
- Strengthen testing (unit, integration with Testcontainers, bounded e2e with Kafka+DB outages, DLQ processing)
- Finalize Analytics service KPIs/dashboards and enrich metrics
- Infrastructure hardening (CI/CD, alerting, perf and scale tests, DB migrations)

---

## Service‑by‑Service Implementation Status
Legend: ✅ Implemented | 🚧 Partial | ❌ Not Implemented | 🔄 Needs refactor/improvement

### 1) Registry Service
- ✅ Household API
  - Endpoints: GET list, POST create, PUT update (aligned to DB schema: head_of_household_name, address, phone, email, household_size, monthly_income)
  - Health endpoints and readiness checks present via shared health module
- ✅ Event emission (choreography)
  - Emits `registry.household.registered` on create/update
  - Transactional outbox pattern writing to `event_outbox` (publisher loop runs and publishes to Kafka)
- ✅ Idempotency/robustness
  - Outbox publisher polls and marks `processed_at`; batch size and polling interval are configurable in code
- 🔄 Improvements
  - Centralize schema migrations (Alembic) instead of manual SQL bootstrap
  - Validate payloads more strictly (types/ranges) and surface 4xx errors consistently
  - Extend metrics (latency histograms; DB errors; outbox lag gauge)

### 2) Eligibility Service
- ✅ Consumer of `registry.household` topic
  - Processes household events; simple rules (income threshold) for approved/denied
  - Persists to `eligibility_assessments` with JSON criteria
- ✅ Event emission
  - Emits `eligibility.assessed.{approved|denied}` via transactional outbox table `event_outbox`
- ✅ Idempotency
  - Uses `processed_events` table; commits only after successful handling
- 🔄 Improvements
  - Formalize rules engine or policy abstraction; parametrize thresholds via config
  - Add richer metrics (processing latency, decision distribution, DLQ counts)
  - Add retries/backoff patterns around DB and Kafka operations

### 3) Payment Service
- ✅ Consumer of `eligibility.assessed` (approved)
  - Schedules payments; persists to `payments` table
  - Emits `payment.scheduled` via outbox
- 🚧 Payment lifecycle
  - `payment.completed` path is stub/assumed; reconciliation/settlement flows not present
- 🔄 Improvements
  - Add status transitions (scheduled → completed/failed), reconciliation jobs, and idempotent updates
  - Add fraud/risk checks placeholders and failure DLQ handling with visibility
  - Expose payment query endpoints and filters for program ops

### 4) Analytics Service
- ✅ Streaming aggregation
  - Consumes `eligibility.assessed.*` and `payment.*`; increments counters in MongoDB
- ✅ API
  - `/api/v1/analytics/summary` returns live counters (assessed, approved, payments_scheduled, payments_completed)
- 🔄 Improvements
  - Expand metrics beyond counters (rates, rolling windows, per-region/program cuts)
  - Provide dashboard JSONs/Grafana provisioning; align topic taxonomy and dimensions
  - Add data retention and backfill jobs (daily rollups)

### 5) Identity Service
- 🚧 Service presence
  - Dockerfile exists; identity endpoints and full IAM flows (signup, token issuance, RBAC/ABAC) are not implemented here; services expect JWT/JWKS
- ❌ Edge OIDC/JWT enforcement
  - Kong/JWT plugin/OIDC verification at the gateway is partially configured in CI expectations but not fully wired
- 🔄 Improvements
  - Choose path: external IdP (Keycloak/Authentik) vs. internal stub
  - Implement JWKS verification at services (prod) and enable Kong JWT plugin / OIDC at edge

---

## Cross‑Cutting Concerns

### Security
- 🚧 Dev-only bypass enabled (`ALLOW_INSECURE_LOCAL`) to ease local testing
- ✅ JWT-based middleware and bearer optionality (dev) implemented
- 🔄 Actions
  - Enforce JWT in all non-dev envs; remove/bury bypass behind explicit env and CI checks
  - Configure Kong with JWT/OIDC verification; require `traceparent` propagation and minimum claims
  - Secret management (env var sourcing via Vault/SOPS/GitHub Encrypted Secrets); scrub logs

### Observability
- ✅ OTEL tracing init hooks; Kafka header propagation; Prometheus metrics in services
- 🚧 Dashboards/alerts (Grafana/Prometheus) outlined in docs; need concrete rules and SLOs
- 🔄 Actions
  - Add latency histograms on API and consumer paths; outbox lag metrics
  - Provide ready-to-use Grafana dashboards and alert rules; add consumer lag exporter

### Data/Migrations
- 🚧 DB bootstrap via SQL; `processed_events` and various indices not formalized as migrations
- 🔄 Actions
  - Introduce Alembic migrations per service; codify schema; add constraints and indexes (FKs, unique, performance)

### Testing
- ✅ CI exists with per-service tests and basic gateway checks; perf smoke via k6 harness
- 🚧 Unit coverage and e2e integration with Testcontainers; DLQ/idempotency coverage limited
- 🔄 Actions
  - Expand unit tests; add Testcontainers Kafka/Postgres-based e2e (bounded runtime < 5m)
  - Add chaos tests (Kafka/DB outages) and DLQ reprocessor tests

### Reliability & Scale
- 🚧 Backpressure and retry policies: basic; consumer lag monitoring and DLQ reprocess strategy need hardening
- 🔄 Actions
  - Add exponential backoff, circuit breakers, and retry budgets on external calls
  - Add DLQ reprocessor service with metrics and admin endpoints
  - Horizontal scaling guidance and partition strategies per topic

---

## Priority Matrix (Next Development Phases)
Priority keys: Critical (P0), High (P1), Medium (P2), Low (P3)

- P0 (Critical)
  - Enforce authentication (disable dev bypass outside local); Kong JWT/OIDC at edge
  - Alembic migrations for all services; align schemas and indices
  - Expand CI: unit + e2e Testcontainers for saga; prevent regressions
- P1 (High)
  - Payment lifecycle completion (complete/cancel/retry + reconciliation)
  - Observability completion: dashboards, alerts, consumer lag exporter
  - DLQ reprocessor (consume *.dlq, retry/backoff, metrics)
  - Eligibility rules abstraction and configuration
- P2 (Medium)
  - Analytics dimensional metrics and Grafana provisioning
  - API surfaces for payment queries; pagination and filtering
  - Performance profiling and k6 thresholds in CI
- P3 (Low)
  - Documentation deepening (runbooks, SLOs, incident response)
  - Admin tooling (replay tools, outbox inspector)

---

## Technical Debt Backlog (with Rough Effort)
Effort guide: S (≤1 day), M (2–3 days), L (4–7 days)

1. Enforce JWT in services and configure Kong OIDC/JWT (P0) — M
2. Remove or guard dev bypass outside local; CI check (P0) — S
3. Introduce Alembic migrations (all services) and codify schema (P0) — L
4. Saga e2e tests with Testcontainers (Kafka+Postgres+Mongo) and idempotency/DLQ coverage (P0) — M
5. Payment lifecycle: complete/cancel/retry + reconciliation (P1) — L
6. DLQ reprocessor service with metrics and ops endpoints (P1) — M
7. Observability: dashboards, alert rules, lag exporter integration (P1) — M
8. Eligibility rules abstraction + config (P1) — M
9. Analytics: dimensional KPIs and Grafana provisioning (P2) — M
10. API hardening: pagination/filters/validation/error contracts (P2) — S
11. Performance tests (k6) with CI gates (P2) — S
12. Secrets management & policy (Vault/SOPS) (P2) — M

---

## Recommended Roadmap (Next 2–3 Sprints)
Each sprint assumed ~2 weeks; adjust by team size/velocity.

### Sprint 1 (Stabilize & Secure)
- P0: Enforce JWT in services; wire Kong JWT/OIDC; disable bypass outside local
- P0: Introduce Alembic migrations and align all DB schemas (Registry, Eligibility, Payment)
- P0: Add Testcontainers-based e2e saga test (bounded <5m) incl. idempotency
- P1: Observability MVP dashboards and critical alerts; add consumer lag exporter
- Deliverables: Passing CI with new tests; JWT enforced in non-dev; baseline dashboards/alerts

### Sprint 2 (Reliability & Payments)
- P1: Payment lifecycle completion (scheduled→completed; reconciliation and retries)
- P1: DLQ reprocessor service + metrics; integrate into dashboards
- P1: Eligibility rules module; thresholds via config
- P2: Expand analytics counters to dimensional metrics and publish Grafana JSON dashboards
- Deliverables: Reliable payments path; DLQ flow visible; configurable eligibility

### Sprint 3 (Scale & Operate)
- P2: Performance tests (k6) with acceptance thresholds in CI
- P2: API hardening (pagination, validation, error schemas) + documentation updates
- P2: Secrets management improvements (Vault/SOPS); scrub logs; rotate creds
- P3: Runbooks (incident response, on-call), SLO definitions and alerts
- Deliverables: Repeatable performance checks; production-ready runbooks and SLOs

---

## References
- docs/OBSERVABILITY_README.md — Observability stack guidance
- .github/workflows/ci.yml — CI pipeline for services and smoke/perf steps
- DSRS_Single_Source_of_Truth.md — Consolidated requirements
- DSRS_Implementation_Plan_Completed_Code_Blocks.markdown — Architecture/code examples
- DSRS_Implementation_Plan_Continued_Code_Blocks.markdown — Roadmap and advanced configs



