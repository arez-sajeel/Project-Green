
from fastapi import APIRouter, Depends
from backend.core.security import get_current_user

router = APIRouter(prefix="/devices", tags=["Device Usage"])

@router.get("/{device_id}/usage")
def get_device_usage(device_id: int, user=Depends(get_current_user)):
    return {
        "device_id": device_id,
        "name": "Boiler",
        "total_kwh": 400,
        "total_cost": 80
    }
