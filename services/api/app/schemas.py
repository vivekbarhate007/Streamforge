from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str


class OverviewMetrics(BaseModel):
    total_users: int
    total_events: int
    total_revenue: Decimal
    conversion_rate: Decimal
    events_last_hour: int
    revenue_today: Decimal


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float


class EventsTimeSeries(BaseModel):
    data: List[TimeSeriesPoint]


class RevenueTimeSeries(BaseModel):
    data: List[TimeSeriesPoint]


class TopProduct(BaseModel):
    product_id: str
    product_name: str
    revenue: Decimal
    quantity: int
    orders: int


class TopProducts(BaseModel):
    products: List[TopProduct]


class QualityCheck(BaseModel):
    checkpoint_name: str
    run_time: datetime
    success: bool
    expectations_passed: int
    expectations_failed: int
    failed_expectations: List[str]


class PipelineStatus(BaseModel):
    pipeline_name: str
    last_run_ts: Optional[datetime]
    status: Optional[str]
    rows_processed: Optional[int]
    lag_seconds: Optional[int]


class HealthStatus(BaseModel):
    pipelines: List[PipelineStatus]
    table_counts: dict
    last_dbt_run: Optional[datetime]
    last_ge_run: Optional[datetime]
