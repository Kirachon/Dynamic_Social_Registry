# DSRS Security Hardening – Next Steps

## Objective
Prepare staging/prod for secure operation by enforcing OIDC at the gateway, disabling insecure dev bypass, and adding core observability.

## Actions
- Kong OIDC (Keycloak)
  - Provide dsrs-secrets with OIDC_CLIENT_ID / OIDC_CLIENT_SECRET
  - Set dsrs-config ISSUER to Keycloak realm URL
  - Apply infra/k8s/kong.yaml
- Disable dev bypass
  - Ensure ALLOW_INSECURE_LOCAL is NOT present in staging/prod overlays (it is not included now)
  - Services rely on JWKS verify in dsrs_common.security
- OTEL/Prometheus
  - Apply infra/k8s/otel-collector.yaml
  - Deploy Prometheus via kube-prometheus-stack (Helm) and scrape services
- Kafka + DLQ worker
  - Ensure KAFKA_BROKERS set in overlays
  - Apply infra/k8s/dlq-reprocessor-deployment.yaml

## Validation
- Use a real JWT from Keycloak; access via Kong; verify 200 for protected endpoints
- Check OTEL collector receives spans; Prometheus can scrape targets
- Simulate DLQ entry and verify reprocessor republishes to main topic

