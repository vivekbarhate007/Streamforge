# High Availability & Resilience

## 1. Load Balancing with Nginx

```nginx
# nginx/nginx.conf
upstream api_backend {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health checks
        proxy_next_upstream error timeout http_500 http_502 http_503;
    }
    
    location /health {
        access_log off;
        proxy_pass http://api_backend/health;
    }
}
```

---

## 2. PostgreSQL Replication

### docker-compose.yml for Replication

```yaml
postgres-primary:
  image: postgres:15
  environment:
    POSTGRES_REPLICATION_MODE: master
    POSTGRES_REPLICATION_USER: replicator
    POSTGRES_REPLICATION_PASSWORD: replicator_password
  volumes:
    - postgres-primary-data:/var/lib/postgresql/data

postgres-replica:
  image: postgres:15
  environment:
    POSTGRES_REPLICATION_MODE: slave
    POSTGRES_MASTER_HOST: postgres-primary
    POSTGRES_REPLICATION_USER: replicator
    POSTGRES_REPLICATION_PASSWORD: replicator_password
  depends_on:
    - postgres-primary
```

---

## 3. Kafka Cluster Setup

```yaml
# docker-compose.yml
kafka1:
  image: confluentinc/cp-kafka:latest
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:9092

kafka2:
  image: confluentinc/cp-kafka:latest
  environment:
    KAFKA_BROKER_ID: 2
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:9092

kafka3:
  image: confluentinc/cp-kafka:latest
  environment:
    KAFKA_BROKER_ID: 3
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:9092
```

---

## 4. Circuit Breaker Pattern

```python
# services/api/app/circuit_breaker.py
from circuitbreaker import circuit
import time

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_external_service():
    # Your external service call
    pass

# Usage
try:
    result = await call_external_service()
except Exception as e:
    logger.error(f"Circuit breaker open: {e}")
    # Fallback logic
```

---

## 5. Retry Logic with Exponential Backoff

```python
# services/api/app/retry.py
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def database_operation():
    # Your database operation
    pass
```

---

## 6. Connection Pooling

```python
# services/api/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

---

## 7. Graceful Shutdown

```python
# services/api/app/main.py
import signal
import asyncio

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down gracefully...")
    # Close database connections
    # Finish processing requests
    # Clean up resources
```

---

## 8. Kubernetes Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        image: streamforge-api:latest
        ports:
        - containerPort: 8000
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
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

