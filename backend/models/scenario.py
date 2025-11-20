# backend/models/scenario.py

# This file defines the Pydantic models required for
# the Sprint 3 & 4 optimisation scenario logic.
# We define this structure once
# to be used by the API router and the OptimisationEngine.

# --- START OF MODIFICATION (SPRINT 4.2) ---
# We need 'List' for the response model
from pydantic import BaseModel
from datetime import datetime
from typing import List
# --- END OF MODIFICATION (SPRINT 4.2) ---

class ShiftValidationRequest(BaseModel):
    """
    Defines the user's proposed load shift input.
    This model is the primary input for the optimisation orchestrator.
    """
    # Note: device_id is 'int' based on backend/models/property.py
    device_id: int
    original_timestamp: datetime  # The "peak" time to move from
    new_timestamp: datetime     # The "off-peak" time to move to

# --- START OF MODIFICATION (SPRINT 4.2) ---
# We now define the *output* models for the API response.

class UsageDataPoint(BaseModel):
    """
    Represents a single data point in a usage curve (FR3.1).
    This model is used to send time-series data to the frontend
    for visualisation.
    
    Adheres to NFR-U2 (Clarity) by using clear, descriptive names
    that the frontend can easily interpret.
    """
    timestamp: datetime
    kwh_consumption: float
    kwh_cost: float

class OptimisationReport(BaseModel):
    """
    Defines the final JSON response for the optimisation report (FR4.2).
    This model packages all metrics and the full predicted usage
    curve into a single, validated object.
    """
    # The primary metric: (Cost Before) - (Cost After)
    estimated_savings: float
    
    # Contextual costs for the frontend
    baseline_cost: float
    scenario_cost: float
    
    # The full data series for the "Predicted Usage Curve"
    # This directly supports the frontend data visualisation (FR3.1)
    predicted_usage_curve: List[UsageDataPoint]

# --- END OF MODIFICATION (SPRINT 4.2) ---