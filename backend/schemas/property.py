from pydantic import BaseModel
from typing import Optional

class PropertyBase(BaseModel):
    property_type: str
    location: str
    tariff_type: Optional[str] = None
    average_monthly_kwh: Optional[int] = None
    solar_panels: Optional[bool] = False
    occupancy: Optional[int] = None
    maintenance_cost: Optional[int] = None
    budget: Optional[int] = None
    carbon_goal: Optional[str] = None

class PropertyResponse(PropertyBase):
    id: str

