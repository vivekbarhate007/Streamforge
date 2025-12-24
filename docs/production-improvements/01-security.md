# Production Security Improvements

## 1. Rate Limiting

### FastAPI Rate Limiting Implementation

```python
# services/api/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/metrics/overview")
@limiter.limit("100/minute")
async def get_overview(...):
    ...
```

### Requirements
```bash
# services/api/requirements.txt
slowapi==0.1.9
```

---

## 2. Enhanced CORS Configuration

```python
# services/api/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],  # Specific domains, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specific methods
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)
```

---

## 3. Input Validation & Sanitization

```python
# services/api/app/schemas.py
from pydantic import BaseModel, validator, Field
import re

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username contains invalid characters')
        return v
```

---

## 4. SQL Injection Prevention

Already using SQLAlchemy ORM (good!), but ensure:

```python
# ✅ GOOD - Parameterized queries
result = db.query(User).filter(User.id == user_id).first()

# ❌ BAD - Never do this
query = f"SELECT * FROM users WHERE id = {user_id}"
```

---

## 5. Secrets Management

### Using Environment Variables (Current - OK for small scale)

### Using AWS Secrets Manager

```python
# services/api/app/secrets.py
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
db_secret = get_secret('streamforge/database')
```

---

## 6. HTTPS/TLS Configuration

### Nginx Reverse Proxy

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 7. Container Security

### Dockerfile Improvements

```dockerfile
# Use non-root user
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app as non-root
COPY --chown=appuser:appuser . /app
USER appuser

WORKDIR /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 8. Database Security

### PostgreSQL Configuration

```sql
-- Enable SSL
ALTER SYSTEM SET ssl = on;

-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE streamforge TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
```

### Connection String with SSL

```python
# services/api/app/db.py
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
```

---

## 9. API Key Management

```python
# services/api/app/auth.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

---

## 10. Security Headers

```python
# services/api/app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

