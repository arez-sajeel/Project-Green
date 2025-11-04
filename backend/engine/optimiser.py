# This file defines the core business logic class for the system,
# as per the UML Class Diagram and Flowchart (Task 1.d: Engine Class Setup).
# All calculation logic (Sprints 2, 3, 4) will live here.

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# Use absolute imports from 'backend' to be discoverable by pytest
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
# ---------------------

class OptimisationEngine:
    """
    The core intelligence class for the Green Energy Optimiser.
    This class ingests context (Property, Tariff) and data (Usage)
    and provides all calculation and recommendation logic.
    """
    
    def __init__(self, property_context: Property, tariff_context: Tariff, usage_data: List[HistoricalUsageLog]):
        self.property: Property = property_context
        self.tariff: Tariff = tariff_context
        self.raw_usage_logs: List[HistoricalUsageLog] = usage_data
        
        # --- Internal State Properties for Calculations ---
        self.baseline_usage_curve: Optional[pd.DataFrame] = None
        self.baseline_cost: float = 0.0
        self.scenario_usage_curve: Optional[pd.DataFrame] = None
        self.scenario_cost: float = 0.0
        self.estimated_savings: float = 0.0

    # --- Sprint 4: Orchestration ---
    def run_scenario_prediction(self, device_id: int, original_time: datetime, new_time: datetime) -> Dict:
        """
        Main orchestrator for [Task 4.c: Orchestrate API Endpoint].
        This method chains all required tasks from Sprints 2 and 3
        to generate the final savings estimate (FR4.2).
        """
        
        # [Sprint 2: Validate Shift Input]
        if not self.validate_shift_input(device_id, new_time):
            raise ValueError("Invalid shift: Device not found or is not shiftable.")
        
        # [Sprint 2: Create Baseline Curve]
        self.baseline_usage_curve = self.create_timestamped_curve(self.raw_usage_logs)
        
        # [Sprint 3: Calculate Baseline Cost]
        self.baseline_cost = self.calculate_total_cost(self.baseline_usage_curve)
        
        # [Sprint 3: Simulate Load Subtraction]
        temp_curve = self.simulate_load_subtraction(
            self.baseline_usage_curve, 
            device_id, 
            original_time
        )
        
        # [Sprint 3: Simulate Load Addition]
        self.scenario_usage_curve = self.simulate_load_addition(
            temp_curve, 
            device_id, 
            new_time
        )
        
        # [Sprint 3: Calculate Scenario Cost]
        self.scenario_cost = self.calculate_total_cost(self.scenario_usage_curve)
        
        # [Task 4a: Calculate Final Savings]
        self.estimated_savings = self.calculate_final_savings(
            self.baseline_cost, 
            self.scenario_cost
        )
        
        # [Task 4b: Structure JSON Output]
        return self.structure_json_output()

    # --- Sprint 2: Retrieval Methods ---
    
    def validate_shift_input(self, device_id: int, new_time: datetime) -> bool:
        """
        Stub for [Sprint 2: Validate Shift Input].
        Checks if a device exists and is marked as 'is_shiftable'.
        """
        device = self._get_device_by_id(device_id)
        if device and device.is_shiftable:
            # TODO: Add logic to check if 'new_time' is valid (e.g., not in the past)
            return True
        return False

    def create_timestamped_curve(self, usage_logs: List[HistoricalUsageLog]) -> pd.DataFrame:
        """
        Implementation for [Sprint 2: Create Baseline Curve].
        
        Converts raw log data into a structured Pandas DataFrame and
        calculates the cost for each timestamp using the class's tariff.
        This fulfils the "Cost Before Scenario" requirement.
        """
        # Adhering to P2 (Readability), we build a simple list of
        # dictionaries first, which is a clear way to construct a DataFrame.
        data_for_df = []
        
        for log in usage_logs:
            # Use the `calculate_cost` method from the Tariff model (Step 1)
            # We use `self.tariff` as the engine is initialised with it.
            calculated_cost = self.tariff.calculate_cost(
                kwh_consumption=log.kwh_consumption,
                timestamp=log.timestamp
            )
            
            data_for_df.append({
                "timestamp": log.timestamp,
                "kwh_consumption": log.kwh_consumption,
                "kwh_cost": calculated_cost # This is the newly calculated cost
            })
        
        # Convert the list of data into a DataFrame
        curve_df = pd.DataFrame(data_for_df)
        
        # Set the timestamp as the index for easier time-series analysis
        # in Sprint 3.
        if not curve_df.empty:
            curve_df.set_index("timestamp", inplace=True)
            
        return curve_df

    # --- Sprint 3: Calculation Methods ---
    
    def calculate_total_cost(self, usage_curve: pd.DataFrame) -> float:
        """
        Stub for [Sprint 3: Calculate Baseline/Scenario Cost].
        Calculates the total cost from a given usage curve.
        """
        # In a real implementation, this would sum the 'kwh_cost' column.
        # For the stub, we return 0.0.
        print("Stub: Calculating total cost...")
        return 0.0

    # --- START OF MODIFICATION (SPRINT 3.2) ---
    def simulate_load_subtraction(self, usage_curve: pd.DataFrame, device_id: int, time: datetime) -> pd.DataFrame:
        """
        Implementation for [Sprint 3: Simulate Load Subtraction].
        
        Removes a device's load from the baseline curve at a specific time
        and recalculates the cost for that single timestamp.
        """
        # First, get the device from the property context
        device = self._get_device_by_id(device_id)
        
        # If device isn't found (should be caught by validation,
        # but good to double check - NFR-S3)
        if not device:
            print(f"Warning (S3.2): Device {device_id} not found. No subtraction performed.")
            return usage_curve.copy() # Return original curve

        # Make a copy to prevent mutating the original DataFrame (NFR-S3)
        temp_curve = usage_curve.copy()

        # Per API-info.docx, all data is half-hourly (HH).
        # Energy (kWh) = Power (kW) * Time (h)
        # We assume the average_draw_kW is for a full hour, so we take 0.5 (30 mins).
        energy_to_subtract_kwh = device.average_draw_kW * 0.5

        try:
            # 1. Get current consumption at the specified time
            # We use .loc[] to access the row by its timestamp index
            current_consumption = temp_curve.loc[time, 'kwh_consumption']
            
            # 2. Calculate new consumption
            new_consumption = current_consumption - energy_to_subtract_kwh
            # Ensure consumption doesn't go below zero
            new_consumption = max(0.0, new_consumption)
            
            # 3. Recalculate cost for this *new* consumption
            new_cost = self.tariff.calculate_cost(
                kwh_consumption=new_consumption,
                timestamp=time
            )
            
            # 4. Update the DataFrame at that specific timestamp
            temp_curve.loc[time, 'kwh_consumption'] = new_consumption
            temp_curve.loc[time, 'kwh_cost'] = new_cost

        except KeyError:
            # Handle error if the specified 'time' is not in the DataFrame index
            # This adheres to P3 (Explicit Error Handling)
            print(f"Warning (S3.2): Timestamp {time} not found in usage curve. No subtraction performed.")
            # In a real API, we might raise an HTTPException here
        
        return temp_curve
    # --- END of MODIFICATION (SPRINT 3.2) ---

    def simulate_load_addition(self, usage_curve: pd.DataFrame, device_id: int, time: datetime) -> pd.DataFrame:
        """
        Stub for [Sprint 3: Simulate Load Addition].
        Adds a device's load to the baseline curve at a new time.
        """
        # TODO: Implement numpy/pandas logic to find the 'time' index,
        # add the device's 'average_draw_kW', and recalculate 'kwh_cost'
        # based on the tariff's 'rate_schedule'.
        print(f"Stub: Adding device {device_id} load at {time}...")
        return usage_curve.copy() # Return a copy to avoid mutation

    # --- Sprint 4: Deployment Methods ---
    
    def calculate_final_savings(self, cost_before: float, cost_after: float) -> float:
        """
        Implementation for [Task 4a: Calculate Final Savings].
        Calculates the simple difference between baseline and scenario costs.
        """
        savings = cost_before - cost_after
        self.estimated_savings = savings
        return savings

    def structure_json_output(self) -> Dict:
        """
        Stub for [Task 4b: Structure JSON Output].
        Packages the results into the final API response object (FR4.2).
        """
        return {
            "estimated_savings": self.estimated_savings,
            "baseline_cost": self.baseline_cost,
            "scenario_cost": self.scenario_cost,
            # TODO: Add data for the "Predicted Usage Curve" visualization
            "scenario_curve_data": [] 
        }

    # --- Helper Methods ---
    
    def _get_device_by_id(self, device_id: int) -> Optional[Device]:
        """Internal helper to find a device in the property's list."""
        for device in self.property.devices:
            if device.device_id == device_id:
                return device
        return None

