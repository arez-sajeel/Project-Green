
from fastapi import APIRouter, Depends
from backend.core.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/properties", tags=["Property Analytics"])

@router.get("/{property_id}/analytics")
def get_property_analytics(property_id: int, user=Depends(get_current_user)):
    return {
        "property_id": property_id,
        "total_kwh": 1200,
        "total_cost": 240,
        "devices": [
            {"id": 1, "name": "Boiler", "kwh": 400},
            {"id": 2, "name": "Heater", "kwh": 300},
        ]
    }
