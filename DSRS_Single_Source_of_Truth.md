# Dynamic Social Registry System (DSRS) — Single Source of Truth

This document consolidates and normalizes the DSRS materials into a definitive reference for development and operations.

## 1. Executive Overview
- Mission: Build a dynamic registry to unify social protection delivery across programs, ensuring inclusive, efficient, secure services.
- Top targets: 99.9% uptime, p95 < 500ms, 20M households, 15+ integrated programs, 30% admin cost reduction, +40% targeting accuracy.
- Principles: Cloud-native, microservices, Zero Trust, event-driven, accessibility and inclusivity by design, observability-first.

## 2. Scope and Stakeholders
- In-scope: Core registry, identity, eligibility, payments, analytics, mobile apps, disaster-response.
- Out-of-scope: Legacy decommissioning; physical infra upgrades.
- Stakeholders: DSWD, beneficiaries, social workers, partner agencies (DOH/DepEd/DOLE/DA/DILG), financial orgs, civil society, international partners.

## 3. Architecture (Canonical)
- Presentation: Web portal (Next.js), mobile apps (React Native/Flutter), USSD/SMS, partner portals.
- API Gateway: Kong (OAuth2/JWT; rate limiting; transformations; versioning).
- Service Mesh: Istio (mTLS, retries, timeouts, canary/blue-green, tracing via Jaeger).
- Services: Identity, Registry, Eligibility, Payment, Analytics, Workflow, Document, Notification, Audit, Reporting.
- Data: PostgreSQL (transactional), MongoDB (document), Redis (cache/session), Elasticsearch (search/logs), Data Lake/Warehouse (BigQuery).
- Events: Kafka (event sourcing, CQRS, saga orchestration), at-least-once.
- Cloud: GCP primary (GKE, Cloud SQL/Spanner, Storage, BigQuery, Dataflow, Vertex AI); Azure for DR (ASR, Blob, ExpressRoute).

## 4. Security & Privacy (Canonical)
- Zero Trust: continuous auth, device/location checks; RBAC + ABAC; least privilege.
- Identity: Keycloak + Spring Security; OAuth2/JWT; MFA (OTP/SMS/Biometrics).
- Crypto: KMS-managed AES-256 at rest; TLS 1.3 in transit; column-level encryption for sensitive fields (PhilSys number, biometrics, bank accounts).
- DLP: Google Cloud DLP for inspection and de-identification; masking/redaction; daily monitoring.
- SIEM/SOC: Standardize on Google Chronicle + AuditBoard. Splunk may be used as an optional alternative if mandated.
- Compliance: Philippine Data Privacy Act, PhilSys Act; security certification target ISO 27001, SOC 2.

## 5. DevEx & Operations
- Dev Methodology: SAFe at program level, scrum for teams; 2-week sprints.
- CI/CD: Jenkins (or GitHub Actions), gated releases, canary, blue-green; IaC with Terraform; Helm for deployments.
- Observability: Prometheus/Grafana for metrics, ELK for logs; SLOs and alerting; monthly security tests (ZAP/Burp), quarterly pentests.
- BCP/DR: Multi-region; RTO 15m, RPO 5m; semi-annual failover tests.

## 6. Data Governance
- Council → Stewards → Owners; data quality processes (profiling, cleansing, validation, monitoring) with targets (accuracy > 98%, completeness > 98%).
- Privacy: consent management, minimization, access restriction; semi-annual audits covering flows and access logs.

## 7. Integration Standards
- PhilSys (OAuth2 REST), LandBank/GCash/PayMaya (REST/SFTP as applicable), DepEd/DOH/DOLE APIs.
- Retry/backoff policies, circuit breakers, idempotency; versioned APIs (/api/v1).

## 8. Frontend Reference (Prototype)
- Tech: Next.js + TypeScript + Tailwind; accessible, neutral government theme; Headless primitives; WCAG 2.1 AA.
- Routes: /operations, /executive, /beneficiary, /field, /programs, /payments, /soc, /analytics, /admin, /quality, /mobile/registration.
- Components: Stat tiles, section cards, responsive tables, placeholders for charts/maps with mock data.
- Accessibility: semantic HTML, keyboard navigation, visible focus rings, reduced motion support, color contrast ≥ AA.

## 9. Performance & Quality Targets
- System: uptime 99.9%, p95 < 500ms, throughput ≥ 1000 TPS, error-rate < 1%.
- Quality: code coverage ≥ 80% (new code ≥ 85%), zero critical vulnerabilities; automation ≥ 78% with a target of 85%.

## 10. Implementation Roadmap (Extract)
- Phase 1 (Foundation): governance, requirements, architecture, environments, CI/CD.
- Phase 2 (Core Dev): Identity, Registry, Eligibility, Payments, Admin/Mobile.
- Phase 3 (Integration): partner APIs, end-to-end testing, performance/security hardening.
- Phase 4 (Pilot): regional pilot, training, support, feedback loop.
- Phase 5 (Rollout): phased regional deployment, handover, knowledge base.

## 11. Tooling Notes (Normalization)
- Analytics visualization: Standardize on BigQuery + Superset for core analytic dashboards; optionally Looker Studio for exec views.
- SIEM/Audit: Prefer Google Chronicle + AuditBoard; Splunk acceptable if required.
- Mapping: Start with static/SVG for prototype; graduate to Leaflet/MapLibre with vector tiles.

## 12. Risks & Mitigations
- Connectivity constraints → offline-first mobile, sync queues, retries.
- Data quality and deduplication → strong validation/dedup services, DQ dashboards.
- Security posture → continuous scanning, hardening baselines, key rotation, zero trust enforcement.

## 13. References to Source Materials
- All detailed YAML/Java/Python examples are retained in:
  - DSRS_Implementation_Plan_Completed_Code_Blocks.markdown
  - DSRS_Implementation_Plan_Continued_Code_Blocks.markdown
  - Dynamic_Social_Registry_System_Book_Structured.md
  - dsrs-dashboard-wireframes.md

## 14. Change Control
- This file is the canonical “single source of truth”.
- Changes require review by the Technical Review Board and PMO; version via Git and tagged releases.

