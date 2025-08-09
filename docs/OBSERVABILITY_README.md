# DSRS Observability (OSS)

This repo ships with:
- Prometheus (docker-compose + Helm recommended for K8s)
- Grafana (docker-compose + K8s deployment)
- OpenTelemetry Collector (docker-compose + K8s)

## Local
- Start infra (compose): Prometheus at :9090, Grafana at :3001
- Services export /metrics via FastAPI instrumentator (Registry) and custom metrics for event flows
- Eligibility and Payment now expose histograms/counters for processing

## Kubernetes
- Apply OTEL Collector and Grafana from infra/k8s
- Install kube-prometheus-stack (Helm) for production Prometheus and Grafana; configure scrapes

## Dashboards
- DSRS Events Overview deployed in docker-compose Grafana
- Add panels for:
  - eligibility_processing_seconds (histogram)
  - eligibility_decisions_total{status}
  - payments_scheduled_total, payments_completed_total
  - dsrs_events_published_total, dsrs_events_consumed_total, dsrs_events_failed_total

## Alerts (suggested)
- Kafka consumer lag > N for M minutes
- DLQ message rate > 0 for M minutes
- 5xx rate > threshold for API services

