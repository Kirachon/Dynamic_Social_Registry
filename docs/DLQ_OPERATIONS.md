# DLQ Reprocessor Operations (OSS)

## Overview
The DLQ reprocessor consumes from *.dlq topics and retries publishing to the corresponding main topics with bounded exponential backoff.

## Metrics
Exposed on :8090/metrics (Prometheus):
- dsrs_dlq_processed_total{topic}
- dsrs_dlq_retry_succeeded_total{topic}
- dsrs_dlq_retry_failed_total{topic}
- dsrs_dlq_retry_seconds (histogram)

## Health
- Liveness: :8090/healthz/liveness (process up)
- Readiness: :8090/healthz/readiness (Kafka connectivity validated via metadata)

## Kubernetes
- Deployment: infra/k8s/dlq-reprocessor-deployment.yaml
  - Includes liveness/readiness probes
  - Port 8090 exposed for metrics/probes

## Alerts
- Prometheus rule examples at infra/otel/alert_rules.yml:
  - DLQBacklogHigh (requires consumergroup lag metric exporter)
  - DLQRetryFailuresHigh
  - DLQReprocessorDown

## Runbook
1. Check DLQ reprocessor health endpoint
2. Check retry failure histograms and rates in Prometheus/Grafana
3. Inspect Kafka cluster and topics for backlog
4. If failures persist, isolate poison messages for manual handling

