# This file defines the Pydantic models for the core domain entities:
# Property, Device, Homeowner, and PropertyManager.
# These models map to the UML Class Diagram and support core functional requirements
# like FR1.3 (Property Data) and FR4.1 (Device Shifting).

from pydantic import BaseModel
from typing import List, Optional
from .user import UserBase, UserRole # Relative import from models/user.py

class Device(BaseModel):
    """
    Represents a high-draw appliance (FR4.1).
    Maps directly to the Device class in the UML diagram.
    This will likely be an embedded list within a Property document.
    """
    device_id: int
    device_name: str
    average_draw_kW: float
    is_shiftable: bool = False # As per UML, with a sensible default

class Property(BaseModel):
    """
    Represents a single unit for metering and tracking (FR1.3).
    Maps to the Property class in the UML diagram.
    This document will be the central record for a single property.
    """
    property_id: int         # Primary key for a Property
    address: str
    location: str
    sq_footage: int
    tariff_id: int           # Foreign key to the Tariff collection

    # This field links a Property to a PropertyManager's portfolio.
    # It is Optional because a Homeowner's property may not be in a portfolio.
    # This is derived from the 1:* relationship in the UML to support FR2.4.
    portfolio_id: Optional[int] = None

    # The 1:* composition relationship from Property to Device in the UML
    # is represented as an embedded list of Device documents.
    devices: List[Device] = []

class Homeowner(UserBase):
    """
    Represents a Homeowner user.
    Inherits from UserBase and fixes the role to HOMEOWNER.
    Links directly to one Property, as per the UML.
    This model defines the data structure for a Homeowner.
    """
    role: UserRole = UserRole.HOMEOWNER
    property_id: int # Foreign key linking to the Property this user owns

class PropertyManager(UserBase):
    """
    Represents a Property Manager user (FR2.4).
    Inherits from UserBase and fixes the role to PROPERTY_MANAGER.
    Links to a portfolio_id, which groups multiple Properties.
    """
    role: UserRole = UserRole.PROPERTY_MANAGER
    portfolio_id: int # ID for the portfolio this user manages
