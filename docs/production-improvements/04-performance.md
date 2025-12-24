# Performance Optimization

## 1. Redis Caching

```python
# services/api/app/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=300)
async def get_overview_metrics(db: Session):
    # Expensive operation
    pass
```

---

## 2. Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_fact_events_ts ON fact_events(ts);
CREATE INDEX idx_fact_events_user_id ON fact_events(user_id);
CREATE INDEX idx_fact_transactions_date ON fact_transactions(date);
CREATE INDEX idx_fact_transactions_user_id ON fact_transactions(user_id);

-- Composite indexes
CREATE INDEX idx_events_user_date ON fact_events(user_id, date(ts));
```

---

## 3. Query Optimization

```python
# Use select_related for joins
from sqlalchemy.orm import selectinload

# ✅ GOOD - Eager loading
users = db.query(User).options(selectinload(User.events)).all()

# ❌ BAD - N+1 queries
users = db.query(User).all()
for user in users:
    events = db.query(Event).filter(Event.user_id == user.id).all()
```

---

## 4. Pagination

```python
# services/api/app/metrics.py
from fastapi import Query

@app.get("/metrics/events")
async def get_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size
    events = db.query(FactEvent)\
        .order_by(FactEvent.ts.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()
    
    total = db.query(func.count(FactEvent.event_id)).scalar()
    
    return {
        "data": events,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size
        }
    }
```

---

## 5. Async Processing

```python
# services/api/app/tasks.py
from celery import Celery

celery_app = Celery('tasks', broker='redis://redis:6379/0')

@celery_app.task
def process_large_dataset(dataset_id):
    # Heavy processing
    pass

# Usage in API
@app.post("/process")
async def trigger_processing():
    task = process_large_dataset.delay(dataset_id)
    return {"task_id": task.id}
```

---

## 6. Response Compression

```python
# services/api/app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 7. Database Connection Pooling

```python
# services/api/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Base pool size
    max_overflow=40,        # Max connections beyond pool_size
    pool_pre_ping=True,    # Verify connections
    pool_recycle=3600,     # Recycle after 1 hour
    echo=False,            # Set to True for SQL logging
)
```

---

## 8. Spark Optimization

```python
# services/spark/jobs/streaming_kafka_to_postgres.py
spark = SparkSession.builder \
    .appName("KafkaToPostgresStreaming") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") \
    .getOrCreate()
```

---

## 9. CDN for Static Assets

```nginx
# nginx.conf
location /static/ {
    alias /var/www/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## 10. Database Query Caching

```python
# Use SQLAlchemy query caching
from sqlalchemy.orm import Query
from sqlalchemy_cache import Cache

cache = Cache()

@cache.cached(timeout=300)
def get_user_metrics(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

