# DSRS Kustomize Overlays and Kong Gateway

This directory provides environment-specific overlays and gateway deployment instructions.

## Overlays
- overlays/dev: development (auth bypass allowed via ALLOW_INSECURE_LOCAL=1, wide CORS)
- overlays/staging: staging (no bypass, strict CORS, secrets-driven URLs, observability)
- overlays/prod: production (no bypass, strict CORS, secrets-driven URLs, observability)

Apply an overlay:

```
kubectl apply -k infra/kustomize/overlays/staging
```

Secrets placeholders must be replaced via real Secret management (External Secrets or kubectl create secret generic ...).

## Kong Gateway
We deploy Kong in Kubernetes using a ConfigMap for declarative configuration and a Deployment/Service:
- Manifest: infra/k8s/kong.yaml (ConfigMap + Deployment + Service)
- Declarative file is embedded as ConfigMap data (kong.yaml) and mounted into the pod

### Environment-specific config
Kong respects env-provided CORS_ALLOW_ORIGINS via the kong Deployment. For per-env values, set CORS_ALLOW_ORIGINS in dsrs-config ConfigMap in your overlay.

### Deploy Kong (staging example)
```
kubectl -n dsrs-staging apply -k infra/kustomize/overlays/staging
kubectl -n dsrs-staging apply -f infra/k8s/kong.yaml
```

Update DNS/Ingress or a load balancer to expose the `kong` Service (port 80) externally.

### Test via Kong
```
# Expect 401 (JWT enforced at gateway)
curl -i http://<KONG_HOST>/registry/api/v1/households
# Health direct to service (cluster-internal or port-forward)
kubectl -n dsrs-staging port-forward svc/registry 8082:80 &
curl -i http://localhost:8082/health
```

### Notes
- JWT plugin is enabled declaratively. Configure real JWT verification (JWKs) with a custom plugin or by issuing signed keys to Kong if not using self-contained verification. For PoC, we enforce standard JWT expiration and issuer claim.
- Rate limiting, bot detection, request size limiting, and CORS are pre-configured. Tune limits per route or service as needed.
- Preserve observability: backend services maintain OTEL/Prometheus; consider Kong ingress controller metrics/tracing for full edge visibility.

