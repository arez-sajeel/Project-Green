
# backend/models/scenario.py

# This new file defines the Pydantic models required for
# the Sprint 3 & 4 optimization scenario logic.
#  we define this structure once
# to be used by the API router and the OptimisationEngine.

from pydantic import BaseModel
from datetime import datetime

class ShiftValidationRequest(BaseModel):
    """
    Defines the user's proposed load shift input.
    This model is the primary input for the optimization orchestrator.
    """
    # Note: device_id is 'int' based on backend/models/property.py
    device_id: int
    original_timestamp: datetime  # The "peak" time to move from
    new_timestamp: datetime     # The "off-peak" time to move to
