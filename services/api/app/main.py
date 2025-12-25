from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.db import get_db, wait_for_db
from app.auth import authenticate_user, create_access_token, get_current_user
from app.settings import settings
from app import metrics, quality, health
from app.schemas import LoginRequest, Token, OverviewMetrics, EventsTimeSeries, RevenueTimeSeries, TopProducts, QualityCheck, HealthStatus
from app.monitoring import metrics_middleware, get_metrics, logger
from app.cache import init_redis

app = FastAPI(title="StreamForge API", version="1.0.0")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Production ready
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://ui:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Monitoring middleware
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    return await metrics_middleware(request, call_next)


# Security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.on_event("startup")
async def startup_event():
    """Wait for database and initialize services on startup"""
    logger.info("Starting StreamForge API...")
    wait_for_db()
    init_redis()
    logger.info("StreamForge API started successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return get_metrics()


@app.post("/auth/login", response_model=Token, summary="User Login", description="Authenticate user and receive JWT access token")
@limiter.limit("10/minute")
async def login(request: Request, credentials: LoginRequest):
    """
    Login endpoint

    - **username**: Username for authentication
    - **password**: Password for authentication

    Returns a JWT access token for authenticated requests.
    """
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/metrics/overview", response_model=OverviewMetrics, summary="Get Overview Metrics", description="Get high-level KPIs including total users, events, revenue, and conversion rate")
@limiter.limit("100/minute")
async def get_overview(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overview metrics

    Returns key performance indicators:
    - Total users
    - Total events
    - Total revenue
    - Conversion rate
    - Events in last hour
    - Revenue today
    """
    return metrics.get_overview_metrics(db)


@app.get("/metrics/events_timeseries", response_model=EventsTimeSeries, summary="Get Events Time Series", description="Get hourly event counts for the specified time period")
@limiter.limit("100/minute")
async def get_events_timeseries(
    request: Request,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back (1-168)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get events time series data

    - **hours**: Number of hours to look back (default: 24, max: 168)

    Returns hourly aggregated event counts as time series data.
    """
    return {"data": metrics.get_events_timeseries(db, hours)}


@app.get("/metrics/revenue_timeseries", response_model=RevenueTimeSeries, summary="Get Revenue Time Series", description="Get daily revenue totals for the specified time period")
@limiter.limit("100/minute")
async def get_revenue_timeseries(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back (1-365)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get revenue time series data

    - **days**: Number of days to look back (default: 30, max: 365)

    Returns daily aggregated revenue totals as time series data.
    """
    return {"data": metrics.get_revenue_timeseries(db, days)}


@app.get("/metrics/top_products", response_model=TopProducts, summary="Get Top Products", description="Get top performing products by revenue")
@limiter.limit("100/minute")
async def get_top_products(
    request: Request,
    limit: int = Query(10, ge=1, le=100, description="Number of top products to return (1-100)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get top products by revenue

    - **limit**: Number of top products to return (default: 10, max: 100)

    Returns products sorted by revenue with quantity and order counts.
    """
    return {"products": metrics.get_top_products(db, limit)}


@app.get("/quality/latest", response_model=QualityCheck, summary="Get Latest Quality Check", description="Get the most recent data quality check results from Great Expectations")
async def get_latest_quality(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latest quality check results

    Returns the most recent Great Expectations checkpoint results including:
    - Checkpoint name
    - Run time
    - Success status
    - Expectations passed/failed counts
    - List of failed expectations (if any)
    """
    return quality.get_latest_quality_check(db)


@app.get("/health/pipelines", response_model=HealthStatus, summary="Get Pipeline Health", description="Get status and health metrics for all data pipelines")
async def get_pipeline_health(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pipeline health status

    Returns comprehensive health information:
    - Pipeline statuses (streaming, batch)
    - Last run timestamps
    - Lag metrics
    - Table row counts
    - Last dbt and Great Expectations run times
    """
    return health.get_health_status(db)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "StreamForge API",
        "version": "1.0.0",
        "docs": "/docs"
    }
