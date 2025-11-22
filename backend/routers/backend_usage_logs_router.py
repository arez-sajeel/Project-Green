
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.data_access.database import get_db
from backend.models.usage import HistoricalUsageLog
from backend.core.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/properties", tags=["Usage Logs"])

@router.get("/{property_id}/usage")
def get_usage_logs(property_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    mock_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "kwh_consumption": 3.5,
            "kwh_cost": 0.72,
            "reading_type": "A"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "kwh_consumption": 2.1,
            "kwh_cost": 0.44,
            "reading_type": "S"
        }
    ]
    return mock_logs
