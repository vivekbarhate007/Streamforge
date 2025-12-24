# Production Deployment Guide

## 1. Kubernetes Deployment

### Complete K8s Manifests

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: streamforge

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: streamforge-config
  namespace: streamforge
data:
  POSTGRES_HOST: "postgres-service"
  KAFKA_BROKER: "kafka-service:9092"
  API_URL: "https://api.yourdomain.com"

---
# k8s/secrets.yaml (use sealed-secrets or external secrets)
apiVersion: v1
kind: Secret
metadata:
  name: streamforge-secrets
  namespace: streamforge
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded>
  API_SECRET_KEY: <base64-encoded>

---
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: streamforge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/streamforge-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: streamforge-config
        - secretRef:
            name: streamforge-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: streamforge
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: streamforge
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 2. Terraform Infrastructure

```hcl
# terraform/main.tf
provider "aws" {
  region = "us-east-1"
}

# ECS Cluster
resource "aws_ecs_cluster" "streamforge" {
  name = "streamforge-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "streamforge-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  
  container_definitions = jsonencode([{
    name  = "api"
    image = "your-registry/streamforge-api:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
  }])
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier     = "streamforge-db"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "streamforge"
  username = "streamforge"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}
```

---

## 3. CI/CD Pipeline

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker compose -f docker-compose.test.yml up --abort-on-container-exit
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t streamforge-api:${{ github.sha }} ./services/api
          docker tag streamforge-api:${{ github.sha }} streamforge-api:latest
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push streamforge-api:${{ github.sha }}
          docker push streamforge-api:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/api api=streamforge-api:${{ github.sha }} -n streamforge
          kubectl rollout status deployment/api -n streamforge
```

---

## 4. Helm Chart

```yaml
# helm/streamforge/values.yaml
replicaCount: 3

image:
  repository: streamforge-api
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80

resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

---

## 5. Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: streamforge-api:latest
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
    environment:
      - DATABASE_URL=${DATABASE_URL}
    networks:
      - streamforge-network

  postgres:
    image: postgres:15
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
    secrets:
      - postgres_password
    networks:
      - streamforge-network

secrets:
  postgres_password:
    external: true

networks:
  streamforge-network:
    driver: overlay
```

---

## 6. Deployment Checklist

- [ ] All secrets moved to secrets management
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Health checks configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] SSL/TLS certificates configured
- [ ] Domain names configured
- [ ] CDN configured for static assets
- [ ] Load balancer configured
- [ ] Auto-scaling configured
- [ ] Log aggregation set up
- [ ] Disaster recovery plan documented
- [ ] Rollback procedure documented

