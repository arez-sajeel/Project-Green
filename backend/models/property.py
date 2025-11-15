
# backend/models/property.py

# This file defines the Pydantic models for the core domain entities:
# Property, Device, Homeowner, and PropertyManager.
#
# MODIFIED (Sprint 2):
# - Imports are now absolute (backend.models.user)
# - Homeowner/PropertyManager now include 'hashed_password'
#   so that they can be used for authentication.

# backend/models/property.py

from pydantic import BaseModel, Field
from typing import List, Optional

# -------------------------------------------------
# FIXED IMPORT (no more backend.)
# -------------------------------------------------
from models.user import UserBase, UserRole
# -------------------------------------------------

class Device(BaseModel):
    """
    Represents a high-draw appliance (FR4.1).
    """
    device_id: int
    device_name: str
    average_draw_kW: float
    is_shiftable: bool = False

class Property(BaseModel):
    """
    Represents a single property in the database.
    """
    property_id: int
    address: str
    location: str
    sq_footage: int
    tariff_id: int
    portfolio_id: Optional[int] = None
    devices: List[Device] = []

class Homeowner(UserBase):
    """
    Homeowner user model.
    """
    role: UserRole = UserRole.HOMEOWNER
    property_id: int
    hashed_password: str

class PropertyManager(UserBase):
    """
    Property Manager user model.
    """
    role: UserRole = UserRole.PROPERTY_MANAGER
    portfolio_id: int
    hashed_password: str

