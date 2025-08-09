# DSRS Security Hardening – Next Steps

## Objective
Enforce JWT at the edge using Kong community plugins while keeping service-side JWKS verification as the authority. Disable insecure dev bypass in non-dev environments and ensure observability remains OSS-only.

## Actions
- Kong Edge Enforcement (community jwt plugin)
  - K8s: infra/k8s/kong.yaml already enables the `jwt` plugin with:
    - claims_to_verify: ["exp"], key_claim_name: iss, secret_is_base64: false
  - Compose (local): infra/docker/kong/kong.yml now enables the same `jwt` plugin to exercise edge enforcement locally.
  - Note: Kong CE `jwt` plugin validates tokens against configured credentials/keys; we rely on service-side JWKS for authoritative validation and use Kong to block missing/expired tokens.
- Service-side JWT/JWKS Authority
  - services/shared/dsrs_common/security.py performs JWKS verification using issuer/audience from env.
  - Do NOT set `ALLOW_INSECURE_LOCAL` in staging/prod overlays. Keep it only for local development convenience.
- OTEL/Prometheus
  - Apply infra/k8s/otel-collector.yaml
  - Deploy Prometheus via kube-prometheus-stack (Helm) and scrape services
- Kafka + DLQ worker
  - Ensure KAFKA_BROKERS set in overlays
  - Apply infra/k8s/dlq-reprocessor-deployment.yaml

## Validation
- Via Kong (no Authorization): protected endpoints return 401.
- Via Kong (valid JWT): protected endpoints return 200; services additionally verify JWKS.
- Check OTEL collector receives spans; Prometheus scrapes targets.
- Simulate DLQ entry and verify reprocessor republishes to main topic.

