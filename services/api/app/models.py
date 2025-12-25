from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date, Text
from sqlalchemy.sql import func
from app.db import Base


class RawEvent(Base):
    __tablename__ = "raw_events"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(100))
    event_type = Column(String(50), nullable=False)
    product_id = Column(String(50))
    price = Column(Numeric(10, 2))
    quantity = Column(Integer)
    metadata_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class RawTransaction(Base):
    __tablename__ = "raw_transactions"

    tx_id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    user_id = Column(String(50), nullable=False)
    product_id = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    country = Column(String(10))
    channel = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class FactEvent(Base):
    __tablename__ = "fact_events"

    event_id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    user_id = Column(String(50), nullable=False)
    session_id = Column(String(100))
    event_type = Column(String(50), nullable=False)
    product_id = Column(String(50))
    price = Column(Numeric(10, 2))
    quantity = Column(Integer)
    date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())


class FactTransaction(Base):
    __tablename__ = "fact_transactions"

    tx_id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False)
    user_id = Column(String(50), nullable=False)
    product_id = Column(String(50), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    revenue = Column(Numeric(10, 2), nullable=False)
    country = Column(String(10))
    channel = Column(String(50))
    date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())


class MetricsDailyKPI(Base):
    __tablename__ = "metrics_daily_kpis"

    date = Column(Date, primary_key=True)
    dau = Column(Integer, default=0)
    events = Column(Integer, default=0)
    purchases = Column(Integer, default=0)
    revenue = Column(Numeric(10, 2), default=0)
    conversion_rate = Column(Numeric(5, 4), default=0)
    updated_at = Column(DateTime, server_default=func.now())


class PipelineHealth(Base):
    __tablename__ = "pipeline_health"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_name = Column(String(100), nullable=False)
    last_run_ts = Column(DateTime)
    status = Column(String(50))
    rows_processed = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
