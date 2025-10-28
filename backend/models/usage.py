
# This file defines the Pydantic model for the HistoricalUsageLog collection.
# This is the most critical schema for performance, designed to be used
# with a MongoDB Time Series Collection, as specified in API-info.docx.
# It supports FR2.5 (Store historical logs), NFR-P1 (Optimization speed),
# and NFR-S2 (Access Control).

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HistoricalUsageLog(BaseModel):
    """
    Represents a single time-series data point for energy consumption (FR2.5).
    This model maps to the 'HistoricalUsageLog' MongoDB time-series collection.
    """
    
    # This is the mandatory time field for the Time Series Collection.
    timestamp: datetime
    
    # Unique meter ID, sourced from UKPN LCL data (per API-info.docx)
    mpan_id: str
    
    # Foreign key to PropertyManager's portfolio
    # Supports NFR-S2 (Access Control) for aggregated queries.
    # Optional because a Homeowner's data might not have one.
    portfolio_id: Optional[str] = None
    
    # The core metric from the UKPN data
    kwh_consumption: float
    
    # Pre-calculated cost for fast dashboarding (FR3.1)
    # This will be calculated in Sprint 3 logic.
    kwh_cost: float
    
    # Supports NFR-S3 (Failure Handling) by logging data state
    reading_type: str # e.g., "A" (Actual), "S" (Simulated)
