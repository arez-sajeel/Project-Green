# This file defines the Pydantic model for the Tariff collection.
# This schema is critical for all cost calculation logic (FR4.1, FR4.2)
# and for supporting tariff comparisons (FR4.3).
# It is based on the detailed schema from API-info.docx.

from pydantic import BaseModel
from typing import Dict
from datetime import datetime

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

    # --- START OF NEW METHODS (SPRINT 2.c) ---

    def get_rate_by_time(self, timestamp: datetime) -> float:
        """
        Calculates the correct cost rate (p/kWh) for a given timestamp.
        
        This implements a simple Time-of-Use (ToU) logic.
        - "peak" is assumed to be between 4 PM (16:00) and 7 PM (19:00).
        - "off_peak" is all other times.

        This directly supports the UML class diagram method.
        """
        # Get the hour from the timestamp (0-23)
        hour = timestamp.hour

        # Define peak hours (4 PM to 7 PM)
        # We check >= 16 and < 19 (e.g., 16:00, 17:00, 18:00 are peak)
        is_peak = 16 <= hour < 19
        
        # Default to 0.0 if neither key exists, as per NFR-S3
        default_off_peak = self.rate_schedule.get("off_peak", 0.0)

        if is_peak:
            # Return peak rate, but fall back to off-peak if "peak" isn't defined
            return self.rate_schedule.get("peak", default_off_peak)
        else:
            # Return off-peak rate
            return default_off_peak

    def calculate_cost(self, kwh_consumption: float, timestamp: datetime) -> float:
        """
        Calculates the total cost for a given amount of consumption (kWh)
        at a specific time.

        This fulfills the `calculate_cost()` method from the UML diagram
        and is the core logic for S2.c.
        """
        # 1. Get the correct rate (p/kWh) for the time
        rate_pkwh = self.get_rate_by_time(timestamp)

        # 2. Calculate final cost (Rate * Consumption)
        # Note: This cost is in pence
        cost = rate_pkwh * kwh_consumption
        
        return cost

    # --- END OF NEW METHODS ---
