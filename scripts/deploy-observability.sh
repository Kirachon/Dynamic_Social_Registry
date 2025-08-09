#!/bin/bash
set -euo pipefail

# DSRS Observability Deployment Script
# Deploys Prometheus, Grafana, and monitoring infrastructure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE=${NAMESPACE:-"dsrs-staging"}
ENVIRONMENT=${ENVIRONMENT:-"staging"}

echo "📊 DSRS Observability Deployment"
echo "   Environment: $ENVIRONMENT"
echo "   Namespace: $NAMESPACE"
echo "   Project Root: $PROJECT_ROOT"
echo ""

# Function to check if kubectl is available and configured
check_kubectl() {
    echo "🔍 Checking kubectl configuration..."
    
    if ! command -v kubectl >/dev/null 2>&1; then
        echo "❌ kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        echo "❌ kubectl is not configured or cluster is not accessible"
        exit 1
    fi
    
    echo "✅ kubectl is configured and cluster is accessible"
    echo ""
}

# Function to create namespace if it doesn't exist
ensure_namespace() {
    echo "🏗️  Ensuring namespace '$NAMESPACE' exists..."
    
    if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
        echo "✅ Namespace '$NAMESPACE' already exists"
    else
        kubectl create namespace "$NAMESPACE"
        echo "✅ Created namespace '$NAMESPACE'"
    fi
    echo ""
}

# Function to deploy Prometheus
deploy_prometheus() {
    echo "📈 Deploying Prometheus..."
    
    # Create ConfigMap for Prometheus configuration
    kubectl create configmap prometheus-config \
        --from-file="$PROJECT_ROOT/infra/prometheus/prometheus.yml" \
        --from-file="$PROJECT_ROOT/infra/prometheus/alert-rules.yml" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy Prometheus
    cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.45.0
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus/'
          - '--web.console.libraries=/etc/prometheus/console_libraries'
          - '--web.console.templates=/etc/prometheus/consoles'
          - '--storage.tsdb.retention.time=200h'
          - '--web.enable-lifecycle'
          - '--web.enable-admin-api'
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus/
        - name: prometheus-storage
          mountPath: /prometheus/
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  labels:
    app: prometheus
spec:
  selector:
    app: prometheus
  ports:
  - name: web
    port: 9090
    targetPort: 9090
EOF
    
    echo "✅ Prometheus deployed"
    echo ""
}

# Function to deploy Grafana
deploy_grafana() {
    echo "📊 Deploying Grafana..."
    
    # Create ConfigMap for Grafana dashboards
    kubectl create configmap grafana-dashboards \
        --from-file="$PROJECT_ROOT/infra/grafana/dashboards/" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create ConfigMap for Grafana provisioning
    kubectl create configmap grafana-provisioning \
        --from-file="$PROJECT_ROOT/infra/grafana/provisioning/" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy Grafana
    cat <<EOF | kubectl apply -n "$NAMESPACE" -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  labels:
    app: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:10.0.0
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin123"  # Change in production
        - name: GF_INSTALL_PLUGINS
          value: "grafana-piechart-panel"
        ports:
        - containerPort: 3000
        volumeMounts:
        - name: grafana-dashboards
          mountPath: /var/lib/grafana/dashboards/dsrs
        - name: grafana-provisioning
          mountPath: /etc/grafana/provisioning
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: grafana-dashboards
        configMap:
          name: grafana-dashboards
      - name: grafana-provisioning
        configMap:
          name: grafana-provisioning
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  labels:
    app: grafana
spec:
  selector:
    app: grafana
  ports:
  - name: web
    port: 3000
    targetPort: 3000
EOF
    
    echo "✅ Grafana deployed"
    echo ""
}

# Function to deploy Kafka lag exporter
deploy_kafka_lag_exporter() {
    echo "📨 Deploying Kafka lag exporter..."
    
    kubectl apply -f "$PROJECT_ROOT/infra/k8s/kafka-lag-exporter.yaml" -n "$NAMESPACE"
    
    echo "✅ Kafka lag exporter deployed"
    echo ""
}

# Function to wait for deployments to be ready
wait_for_deployments() {
    echo "⏳ Waiting for deployments to be ready..."
    
    local deployments=("prometheus" "grafana" "kafka-lag-exporter")
    
    for deployment in "${deployments[@]}"; do
        echo "   Waiting for $deployment..."
        kubectl wait --for=condition=available --timeout=300s deployment/$deployment -n "$NAMESPACE"
    done
    
    echo "✅ All deployments are ready"
    echo ""
}

# Function to display access information
display_access_info() {
    echo "🎉 Observability stack deployed successfully!"
    echo ""
    echo "📋 Access Information:"
    echo "   Namespace: $NAMESPACE"
    echo ""
    echo "   Prometheus:"
    echo "     kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090"
    echo "     Then access: http://localhost:9090"
    echo ""
    echo "   Grafana:"
    echo "     kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000"
    echo "     Then access: http://localhost:3000"
    echo "     Default credentials: admin/admin123"
    echo ""
    echo "   Kafka Lag Exporter:"
    echo "     kubectl port-forward -n $NAMESPACE svc/kafka-lag-exporter 8080:80"
    echo "     Then access: http://localhost:8080/metrics"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View pods: kubectl get pods -n $NAMESPACE"
    echo "   View services: kubectl get svc -n $NAMESPACE"
    echo "   View logs: kubectl logs -f deployment/<service-name> -n $NAMESPACE"
    echo ""
}

# Main execution
main() {
    echo "🚀 Starting DSRS observability deployment..."
    echo ""
    
    # Pre-flight checks
    check_kubectl
    ensure_namespace
    
    # Deploy components
    deploy_prometheus
    deploy_grafana
    deploy_kafka_lag_exporter
    
    # Wait for everything to be ready
    wait_for_deployments
    
    # Display access information
    display_access_info
}

# Run main function
main "$@"
