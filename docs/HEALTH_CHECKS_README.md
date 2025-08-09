# Health Checks & Probes

This adds real readiness checks for DB and Kafka (and Mongo for Analytics) and wires Kubernetes liveness/readiness probes.

Endpoints:
- /healthz/liveness: Fast path confirming process is alive; optionally includes quick DB ping
- /healthz/readiness: Validates DB connectivity and Kafka metadata (Mongo for Analytics)

Kubernetes:
- Probes added to registry, eligibility, payment, analytics Deployments
- Probe config example: infra/k8s/probes.yaml

Notes:
- In constrained dev envs without Kafka/DB, readiness will fail as expected; adjust initial delays and timeouts as needed.
- Extend readiness_check to include dependency-specific checks (e.g., external services) when added.

