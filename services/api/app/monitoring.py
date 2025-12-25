"""Monitoring and metrics for production"""
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'database_active_connections',
    'Number of active database connections'
)


# Structured logging setup
def setup_logging():
    """Setup structured JSON logging"""
    from pythonjsonlogger import jsonlogger

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)

    return logger


logger = setup_logging()


async def metrics_middleware(request, call_next):
    """Middleware to track metrics"""
    start_time = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Track metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        # Log request
        logger.info("Request processed", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration
        })

        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error("Request failed", extra={
            "method": request.method,
            "path": request.url.path,
            "error": str(e),
            "duration": duration
        })
        raise


def get_metrics():
    """Get Prometheus metrics"""
    return Response(content=generate_latest(), media_type="text/plain")
