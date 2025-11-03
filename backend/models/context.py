# backend/models/context.py

# This file defines the Pydantic response model for the /context/ endpoint.
# Adheres to "Mandatory Type Hinting" and provides a clear API contract.
# This data is the output of the "Fetch User Context" (Sprint 2) task.

from pydantic import BaseModel
from typing import List, Dict
from .property import Property  # Import from existing model
from .tariff import Tariff      # Import from existing model

class UserContextResponse(BaseModel):
    """
    Defines the JSON response for the GET /context/ endpoint.
    
    This object provides all the necessary data (user_id, properties,
    and cost rates) for subsequent "Create Timestamped Curve" logic.
    """
    user_id: str
    
    # A list of all properties the user has access to
    # For Homeowners, this will be a list with one item.
    # For PropertyManagers, this will be their full portfolio.
    properties: List[Property]
    
    # A dictionary of all unique tariffs associated with the user's properties.
    # Using a Dict[str, Tariff] allows for O(1) lookup by tariff_id
    # in subsequent logic.
    tariffs: Dict[str, Tariff]
