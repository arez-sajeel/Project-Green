# This file defines the Pydantic model for the Tariff collection.
# This schema is critical for all cost calculation logic (FR4.1, FR4.2)
# and for supporting tariff comparisons (FR4.3).
# It is based on the detailed schema from API-info.docx.

from pydantic import BaseModel
from typing import Dict

class Tariff(BaseModel):
    """
    Represents a single energy tariff plan (FR1.2, FR4.3).
    Maps to the Tariff collection in MongoDB, based on the
    detailed schema in API-info.docx.
    """
    tariff_id: int              # Primary key for a Tariff
    provider_name: str
    
    # From API-info.docx: Sourced from mock data (e.g., MSE)
    payment_type: str           # e.g., "Direct Debit", "Prepayment"
    region: str                 # For modeling regional price variance
    standing_charge_pd: float   # Standing charge in pence per day
    
    # Supports FR4.3: comparison against greener sources
    carbon_score: int           # Simulated score (e.g., 1-100)
    
    # Supports FR1.2, FR4.1: The core Time-of-Use rate map
    # Using Dict[str, float] for flexibility, as described in API-info.docx
    # Example: {"peak": 28.50, "off_peak": 12.75}
    rate_schedule: Dict[str, float]
