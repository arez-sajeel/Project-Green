# backend/models/property.py

# This file defines the Pydantic models for the core domain entities:
# Property, Device, Homeowner, and PropertyManager.
#
# MODIFIED (Sprint 2):
# - Imports are now absolute (backend.models.user)
# - Homeowner/PropertyManager now include 'hashed_password'
#   so that they can be used for authentication.
#
# --- START OF MODIFICATION (SPRINT 4.3 - TEST FIX) ---
# Added `mpan_id` to the Property model to fix the 500 Error.
# --- END OF MODIFICATION (SPRINT 4.3 - TEST FIX) ---

from pydantic import BaseModel, Field
from typing import List, Optional
from backend.models.user import UserBase, UserRole  # FIX: Absolute import


class Device(BaseModel):
    """
    Represents a high-draw appliance (FR4.1).
    Maps directly to the Device class in the UML diagram.
    This will likely be an embedded list within a Property document.
    """

    device_id: int
    device_name: str
    average_draw_kW: float
    is_shiftable: bool = False  # As per UML, with a sensible default


class Property(BaseModel):
    """
    Represents a single unit for metering and tracking (FR1.3).
    Maps to the Property class in the UML diagram.
    This document will be the central record for a single property.
    """

    # Use Field(...) for aliasing the MongoDB '_id' field if needed
    # For now, we'll assume a separate property_id
    property_id: int  # Primary key for a Property
    address: str
    location: str
    sq_footage: int
    tariff_id: int  # Foreign key to the Tariff collection

    # This field links a Property to a PropertyManager's portfolio.
    # It is Optional because a Homeowner's property may not be in a portfolio.
    # This is derived from the 1:* relationship in the UML to support FR2.4.
    portfolio_id: Optional[int] = None

    # The 1:* composition relationship from Property to Device in the UML
    # is represented as an embedded list of Device documents.
    devices: List[Device] = []

    # --- START OF SPRINT 4.3 FIX ---
    # This field is required by the optimiser router to fetch usage logs.
    # It was missing, causing the "mpan_id is missing" 500 Error.
    mpan_id: Optional[str] = None
    # --- END OF SPRINT 4.3 FIX ---


class Homeowner(UserBase):
    """
    Represents a Homeowner user.
    Inherits from UserBase and fixes the role to HOMEOWNER.
    Links directly to one Property, as per the UML.
    This model defines the *full user document* in the 'users' collection.
    """

    role: UserRole = UserRole.HOMEOWNER
    property_id: int  # Foreign key linking to the Property this user owns

    # FIX: This field is required for the login logic to verify the password.
    # It will not be exposed in API responses.
    hashed_password: str


class PropertyManager(UserBase):
    """
    Represents a Property Manager user (FR2.4).
    Inherits from UserBase and fixes the role to PROPERTY_MANAGER.
    Links to a portfolio_id, which groups multiple Properties.
    This model defines the *full user document* in the 'users' collection.
    """

    role: UserRole = UserRole.PROPERTY_MANAGER
    portfolio_id: int  # ID for the portfolio this user manages

    # FIX: This field is required for the login logic to verify the password.
    # It will not be exposed in API responses.
    hashed_password: str