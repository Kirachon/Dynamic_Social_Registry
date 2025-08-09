# DSRS Kustomize Overlays

This directory provides environment-specific overlays for Kubernetes deployments.

- overlays/dev: development (auth bypass allowed, wide CORS, local-ish URLs)
- overlays/staging: staging (no bypass, strict CORS, Secrets-driven URLs, observability enabled)
- overlays/prod: production (no bypass, strict CORS, Secrets-driven URLs, observability enabled)

To build and apply an overlay:

```
kubectl apply -k infra/kustomize/overlays/staging
```

Secrets placeholders must be replaced via real Secret management (External Secrets or kubectl create secret generic ...).

