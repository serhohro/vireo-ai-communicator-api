# Vireo Deployment Guide

Complete guide for deploying Vireo in production environments.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Edge Deployment](#edge-deployment)
7. [Monitoring](#monitoring)
8. [Scaling](#scaling)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Vireo can be deployed in various environments:

| Environment | Use Case | Resources |
|-------------|----------|-----------|
| Development | Testing and development | Minimum |
| Staging | Pre-production validation | Moderate |
| Production | Live deployment | High/Scaling |
| Edge | IoT, mobile, Raspberry Pi | Minimal |

### Deployment Architecture
┌─────────────────────────────────────────────────────────────┐
│ LOAD BALANCER │
│ (Nginx / HAProxy) │
└─────────────────────┬───────────────────────────────────────┘
│
┌─────────────┼─────────────┐
│ │ │
┌───────▼──────┐ ┌─────▼─────┐ ┌───▼────────┐
│ Agent 1 │ │ Agent 2 │ │ Agent N │
│ (Python) │ │ (Rust) │ │(TypeScript)│
└──────────────┘ └───────────┘ └────────────┘
│ │ │
└─────────────┼─────────────┘
│
┌─────────────────────▼───────────────────────────────────────┐
│ MESSAGE BUS │
│ (Redis / RabbitMQ / Kafka) │
└─────────────────────────────────────────────────────────────┘
│
┌─────────────────────▼───────────────────────────────────────┐
│ DATABASE │
│ (PostgreSQL / MongoDB) │
└─────────────────────────────────────────────────────────────┘

text

---

## Local Development

### Python

```bash
# Clone repository
git clone https://github.com/vireo-ai/vireo-ai-communicator-3
cd vireo-ai-communicator-3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Vireo in development mode
pip install -e .

# Run tests
pytest tests/ -v

# Start development server
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
Rust
bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build
cd vireo-ai-communicator-3
cargo build

# Run tests
cargo test

# Run in development
cargo run --bin vireo-server
TypeScript
bash
# Install dependencies
cd vireo-ai-communicator-3/sdk/typescript
npm install

# Build
npm run build

# Run tests
npm test

# Start development server
npm run dev
Docker Deployment
Docker Compose (Development)
yaml
# docker-compose.yml
version: '3.8'

services:
  # Vireo API Server
  vireo-api:
    build:
      context: .
      dockerfile: docker/Dockerfile.python
    container_name: vireo-api
    ports:
      - "8000:8000"
    environment:
      - VIREO_ENV=development
      - VIREO_LOG_LEVEL=debug
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/vireo
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  # Redis Message Bus
  redis:
    image: redis:7-alpine
    container_name: vireo-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: vireo-postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=vireo
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  # Vireo Web Dashboard
  vireo-web:
    build:
      context: .
      dockerfile: docker/Dockerfile.wasm
    container_name: vireo-web
    ports:
      - "3000:3000"
    environment:
      - VIREO_API_URL=http://vireo-api:8000
    restart: unless-stopped

volumes:
  redis-data:
  postgres-data:
Production Dockerfile
dockerfile
# docker/Dockerfile.python (Production)
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install Vireo
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 vireo && chown -R vireo:vireo /app
USER vireo

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "api.server:app", "--bind", "0.0.0.0:8000"]
Docker Commands
bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Scale agents
docker-compose up -d --scale vireo-api=3
Kubernetes Deployment
Kubernetes Manifests
yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vireo-api
  namespace: vireo
  labels:
    app: vireo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vireo-api
  template:
    metadata:
      labels:
        app: vireo-api
    spec:
      containers:
      - name: vireo-api
        image: vireo-api:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: VIREO_ENV
          value: "production"
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: vireo-config

---
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vireo-api-service
  namespace: vireo
spec:
  selector:
    app: vireo-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vireo-ingress
  namespace: vireo
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.vireo.ai
    secretName: vireo-tls
  rules:
  - host: api.vireo.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vireo-api-service
            port:
              number: 80
Helm Chart
yaml
# helm/vireo/values.yaml
replicaCount: 3

image:
  repository: vireo-api
  tag: latest
  pullPolicy: Always

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  host: api.vireo.ai

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 512Mi

config:
  environment: production
  logLevel: info

redis:
  enabled: true
  host: redis-master
  port: 6379

postgres:
  enabled: true
  host: postgres-postgresql
  port: 5432
  database: vireo

storage:
  enabled: true
  size: 10Gi

monitoring:
  enabled: true
  prometheus:
    enabled: true
  grafana:
    enabled: true
Kubernetes Commands
bash
# Create namespace
kubectl create namespace vireo

# Deploy
kubectl apply -f kubernetes/

# Check status
kubectl get pods -n vireo

# View logs
kubectl logs -f deployment/vireo-api -n vireo

# Scale
kubectl scale deployment vireo-api -n vireo --replicas=5

# Update
kubectl set image deployment/vireo-api vireo-api=latest -n vireo

# Rollback
kubectl rollout undo deployment/vireo-api -n vireo
Cloud Deployment
AWS Deployment
python
# deploy/aws.py
import boto3
from vireo.deploy import AWSDeployer

deployer = AWSDeployer(
    region="us-east-1",
    cluster_name="vireo-cluster",
    service_name="vireo-api"
)

# Deploy to ECS
deployer.deploy_ecs(
    task_definition="vireo-task.json",
    desired_count=3,
    min_healthy=2,
    max_percent=200
)

# Set up autoscaling
deployer.setup_autoscaling(
    service_name="vireo-api",
    min_capacity=2,
    max_capacity=10,
    cpu_target=70,
    memory_target=80
)

# Deploy to EKS
deployer.deploy_eks(
    cluster_name="vireo-eks",
    deployment_file="kubernetes/deployment.yaml"
)
GCP Deployment
python
# deploy/gcp.py
from vireo.deploy import GCPDeployer

deployer = GCPDeployer(
    project_id="vireo-project",
    region="us-central1"
)

# Deploy to Cloud Run
deployer.deploy_cloudrun(
    image="gcr.io/vireo-project/vireo-api:latest",
    service_name="vireo-api",
    memory="1Gi",
    cpu=1,
    max_instances=10
)

# Deploy to GKE
deployer.deploy_gke(
    cluster_name="vireo-cluster",
    deployment_file="kubernetes/deployment.yaml"
)
Azure Deployment
python
# deploy/azure.py
from vireo.deploy import AzureDeployer

deployer = AzureDeployer(
    subscription_id="xxx",
    resource_group="vireo-rg",
    location="eastus"
)

# Deploy to ACI
deployer.deploy_aci(
    container_name="vireo-api",
    image="vireo-api:latest",
    cpu_cores=1,
    memory_gb=2
)

# Deploy to AKS
deployer.deploy_aks(
    cluster_name="vireo-aks",
    deployment_file="kubernetes/deployment.yaml"
)
Edge Deployment
Raspberry Pi
bash
# Install on Raspberry Pi
sudo apt-get update
sudo apt-get install python3-pip python3-dev

# Install Vireo
pip3 install vireo-ai

# Install dependencies
pip3 install tensorflow-lite-runtime

# Run agent
python3 -m vireo.agent --config config/edge.json

# Run as service
sudo cp vireo-agent.service /etc/systemd/system/
sudo systemctl enable vireo-agent
sudo systemctl start vireo-agent
Mobile Deployment
python
# mobile/agent.py
from vireo import Agent
from vireo.edge import Quantize

# Quantize model for mobile
quantizer = Quantize(
    precision="int8",
    calibration_data=data
)

# Quantize model
quantized_model = quantizer.quantize(model)

# Create mobile agent
agent = Agent(
    name="MobileAgent",
    model=quantized_model,
    config={
        "memory_limit": "256MB",
        "battery_optimized": True,
        "offline_mode": True
    }
)
ARM64 Deployment
bash
# Build for ARM64
docker build -f docker/Dockerfile.python --platform linux/arm64 -t vireo-api:arm64 .

# Deploy to ARM64
docker run -d --platform linux/arm64 -p 8000:8000 vireo-api:arm64
Monitoring
Prometheus Metrics
python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
messages_total = Counter(
    'vireo_messages_total',
    'Total messages processed',
    ['type', 'agent']
)

message_duration = Histogram(
    'vireo_message_duration_seconds',
    'Message processing duration',
    ['type']
)

active_agents = Gauge(
    'vireo_active_agents',
    'Number of active agents'
)

active_connections = Gauge(
    'vireo_active_connections',
    'Number of active connections'
)

# Record metrics
async def process_message(message):
    start = time.time()
    
    try:
        result = await handle_message(message)
        messages_total.labels(
            type=message.type,
            agent=message.sender
        ).inc()
        return result
    finally:
        message_duration.labels(
            type=message.type
        ).observe(time.time() - start)
Grafana Dashboard
json
{
  "dashboard": {
    "title": "Vireo Monitoring",
    "panels": [
      {
        "title": "Message Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(vireo_messages_total[5m])",
            "legendFormat": "{{type}} - {{agent}}"
          }
        ]
      },
      {
        "title": "Agent Status",
        "type": "stat",
        "targets": [
          {
            "expr": "vireo_active_agents",
            "format": "time_series"
          }
        ]
      },
      {
        "title": "Message Duration",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, vireo_message_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(vireo_errors_total[5m])",
            "legendFormat": "{{type}}"
          }
        ]
      }
    ]
  }
}
Logging Configuration
yaml
# config/logging.yaml
version: 1
formatters:
  json:
    format: '{"timestamp":"%(asctime)s","level":"%(levelname)s","agent":"%(agent)s","message":"%(message)s","extras":%(extras)s}'
  console:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: console
  file:
    class: logging.handlers.RotatingFileHandler
    filename: /var/log/vireo/app.log
    maxBytes: 10485760
    backupCount: 10
    formatter: json
  elk:
    class: vireo.logging.ELKHandler
    host: elasticsearch:9200
    index: vireo-logs
loggers:
  vireo:
    level: INFO
    handlers: [console, file, elk]
Scaling
Horizontal Scaling
python
# scaling/horizontal.py
class HorizontalScaler:
    def __init__(self):
        self.metrics = {
            "cpu": 0,
            "memory": 0,
            "messages_per_second": 0,
            "queue_length": 0
        }
    
    def should_scale(self) -> bool:
        if self.metrics["messages_per_second"] > 1000:
            return True
        if self.metrics["queue_length"] > 500:
            return True
        if self.metrics["cpu"] > 80:
            return True
        return False
    
    def scale_up(self):
        # Add more agents
        agent_id = create_new_agent()
        register_agent(agent_id)
        return agent_id
    
    def scale_down(self):
        # Remove idle agents
        idle_agents = find_idle_agents()
        for agent_id in idle_agents:
            deregister_agent(agent_id)
Load Balancing
python
# scaling/load_balancer.py
class LoadBalancer:
    def __init__(self):
        self.agents = []
        self.strategy = "round_robin"
        self.current = 0
    
    def add_agent(self, agent):
        self.agents.append(agent)
    
    def route_message(self, message):
        if self.strategy == "round_robin":
            return self.round_robin(message)
        elif self.strategy == "least_loaded":
            return self.least_loaded(message)
        elif self.strategy == "consistent_hash":
            return self.consistent_hash(message)
    
    def round_robin(self, message):
        agent = self.agents[self.current % len(self.agents)]
        self.current += 1
        return agent
    
    def least_loaded(self, message):
        return min(self.agents, key=lambda a: a.load)
    
    def consistent_hash(self, message):
        hash_value = hash(message.id)
        index = hash_value % len(self.agents)
        return self.agents[index]
Troubleshooting
Common Issues
bash
# 1. Connection refused
# Check if service is running
docker ps
kubectl get pods

# Check logs
docker logs vireo-api
kubectl logs vireo-api-xxx

# 2. Out of memory
# Increase memory limits
docker update --memory 2g vireo-api

# 3. Slow performance
# Profile the application
python -m cProfile -o profile.stats api/server.py

# Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumtime').print_stats(20)"

# 4. SSL certificate expired
# Renew certificates
kubectl delete secret vireo-tls
kubectl apply -f kubernetes/ingress.yaml
Health Checks
python
# api/health.py
from fastapi import FastAPI
from vireo import get_status

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "timestamp": time.time()
    }

@app.get("/ready")
async def readiness_check():
    # Check dependencies
    redis_ok = check_redis()
    db_ok = check_database()
    
    return {
        "status": "ready" if redis_ok and db_ok else "not_ready",
        "redis": redis_ok,
        "database": db_ok
    }

@app.get("/metrics")
async def metrics():
    return {
        "agents": get_active_agents(),
        "messages": get_message_count(),
        "connections": get_active_connections()
    }
🔗 Next Steps
GPU Guide

WASM Guide

Security Guide

API Reference