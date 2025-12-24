from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
from app.models import PipelineHealth, FactEvent, FactTransaction, RawEvent, RawTransaction
from app.schemas import PipelineStatus, HealthStatus
from typing import List, Dict


def get_pipeline_statuses(db: Session) -> List[PipelineStatus]:
    """Get status of all pipelines"""
    pipelines = []
    
    # Streaming pipeline status
    latest_event = db.query(func.max(FactEvent.ts)).scalar()
    if latest_event:
        lag = (datetime.utcnow() - latest_event).total_seconds()
    else:
        lag = None
    
    # Check if streaming pipeline is active (events within last 10 minutes)
    # Also check if there are any events at all
    event_count = db.query(func.count(FactEvent.event_id)).scalar() or 0
    if event_count > 0 and lag and lag < 600:  # 10 minutes threshold
        status = "running"
    elif event_count > 0:
        status = "idle"  # Has events but not recent
    else:
        status = "pending"  # No events yet
    
    pipelines.append(PipelineStatus(
        pipeline_name="streaming_kafka_to_postgres",
        last_run_ts=latest_event,
        status=status,
        rows_processed=event_count,
        lag_seconds=int(lag) if lag else None
    ))
    
    # Batch pipeline status
    latest_transaction = db.query(func.max(FactTransaction.ts)).scalar()
    pipelines.append(PipelineStatus(
        pipeline_name="batch_csv_to_postgres",
        last_run_ts=latest_transaction,
        status="completed" if latest_transaction else "pending",
        rows_processed=None,
        lag_seconds=None
    ))
    
    return pipelines


def get_table_counts(db: Session) -> Dict[str, int]:
    """Get row counts for key tables"""
    return {
        "raw_events": db.query(func.count(RawEvent.id)).scalar() or 0,
        "raw_transactions": db.query(func.count(RawTransaction.tx_id)).scalar() or 0,
        "fact_events": db.query(func.count(FactEvent.event_id)).scalar() or 0,
        "fact_transactions": db.query(func.count(FactTransaction.tx_id)).scalar() or 0,
    }


def get_health_status(db: Session) -> HealthStatus:
    """Get overall pipeline health status"""
    pipelines = get_pipeline_statuses(db)
    table_counts = get_table_counts(db)
    
    # Get last dbt run (would be stored in pipeline_health table in real implementation)
    last_dbt_run = db.query(func.max(PipelineHealth.last_run_ts)).filter(
        PipelineHealth.pipeline_name == "dbt_run"
    ).scalar()
    
    # Get last GE run
    last_ge_run = db.query(func.max(PipelineHealth.last_run_ts)).filter(
        PipelineHealth.pipeline_name == "great_expectations"
    ).scalar()
    
    return HealthStatus(
        pipelines=pipelines,
        table_counts=table_counts,
        last_dbt_run=last_dbt_run,
        last_ge_run=last_ge_run
    )

