from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from app.schemas import QualityCheck
from typing import List


def get_latest_quality_check(db: Session) -> QualityCheck:
    """Get latest data quality check results"""
    # In a real implementation, this would query Great Expectations results
    # For now, return a mock response
    return QualityCheck(
        checkpoint_name="raw_events_checkpoint",
        run_time=datetime.utcnow(),
        success=True,
        expectations_passed=6,
        expectations_failed=0,
        failed_expectations=[]
    )


def get_quality_history(db: Session, limit: int = 10) -> List[QualityCheck]:
    """Get quality check history"""
    # In a real implementation, this would query stored GE results
    return [get_latest_quality_check(db)]

