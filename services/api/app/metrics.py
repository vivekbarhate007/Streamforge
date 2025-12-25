from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.models import FactEvent, FactTransaction
from app.schemas import OverviewMetrics, TimeSeriesPoint, TopProduct
from typing import List
from decimal import Decimal


def get_overview_metrics(db: Session) -> OverviewMetrics:
    """Get overview KPI metrics"""
    # Total unique users
    total_users = db.query(func.count(func.distinct(FactEvent.user_id))).scalar() or 0

    # Total events
    total_events = db.query(func.count(FactEvent.event_id)).scalar() or 0

    # Total revenue
    total_revenue = db.query(func.coalesce(func.sum(FactTransaction.revenue), 0)).scalar() or Decimal("0")

    # Conversion rate (purchases / total events)
    purchases = db.query(func.count(FactEvent.event_id)).filter(
        FactEvent.event_type == "purchase"
    ).scalar() or 0
    conversion_rate = Decimal(purchases) / Decimal(total_events) if total_events > 0 else Decimal("0")

    # Events in last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    events_last_hour = db.query(func.count(FactEvent.event_id)).filter(
        FactEvent.ts >= one_hour_ago
    ).scalar() or 0

    # Revenue today
    today = datetime.utcnow().date()
    revenue_today = db.query(func.coalesce(func.sum(FactTransaction.revenue), 0)).filter(
        func.date(FactTransaction.ts) == today
    ).scalar() or Decimal("0")

    return OverviewMetrics(
        total_users=total_users,
        total_events=total_events,
        total_revenue=total_revenue,
        conversion_rate=conversion_rate,
        events_last_hour=events_last_hour,
        revenue_today=revenue_today,
    )


def get_events_timeseries(db: Session, hours: int = 24) -> List[TimeSeriesPoint]:
    """Get events time series data"""
    start_time = datetime.utcnow() - timedelta(hours=hours)

    results = db.query(
        func.date_trunc('hour', FactEvent.ts).label('hour'),
        func.count(FactEvent.event_id).label('count')
    ).filter(
        FactEvent.ts >= start_time
    ).group_by('hour').order_by('hour').all()

    return [
        TimeSeriesPoint(timestamp=row.hour, value=float(row.count))
        for row in results
    ]


def get_revenue_timeseries(db: Session, days: int = 365) -> List[TimeSeriesPoint]:
    """Get revenue time series data"""
    # For demo purposes, show all data if days is 365 or more
    if days >= 365:
        # Don't filter by date - show all available data
        results = db.query(
            FactTransaction.date,
            func.sum(FactTransaction.revenue).label('revenue')
        ).group_by(FactTransaction.date).order_by(FactTransaction.date).all()
    else:
        start_date = datetime.utcnow().date() - timedelta(days=days)
        results = db.query(
            FactTransaction.date,
            func.sum(FactTransaction.revenue).label('revenue')
        ).filter(
            FactTransaction.date >= start_date
        ).group_by(FactTransaction.date).order_by(FactTransaction.date).all()

    return [
        TimeSeriesPoint(timestamp=datetime.combine(row.date, datetime.min.time()), value=float(row.revenue))
        for row in results
    ]


def get_top_products(db: Session, limit: int = 10) -> List[TopProduct]:
    """Get top products by revenue"""
    results = db.query(
        FactTransaction.product_id,
        func.sum(FactTransaction.revenue).label('revenue'),
        func.sum(FactTransaction.quantity).label('quantity'),
        func.count(FactTransaction.tx_id).label('orders')
    ).group_by(FactTransaction.product_id).order_by(
        desc('revenue')
    ).limit(limit).all()

    return [
        TopProduct(
            product_id=row.product_id,
            product_name=f"Product {row.product_id}",
            revenue=row.revenue or Decimal("0"),
            quantity=int(row.quantity or 0),
            orders=int(row.orders or 0)
        )
        for row in results
    ]
