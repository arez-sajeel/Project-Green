# This file defines the core business logic class for the system,
# as per the UML Class Diagram and Flowchart (Task 1.d: Engine Class Setup).
# All calculation logic (Sprints 2, 3, 4) will live here.

import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import HTTPException # <-- MODIFIED (S2.4): For error handling (NFR-S3)
import logging # <-- ADDED (S3.1): For logging errors

# Use absolute imports from 'backend' to be discoverable by pytest
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
# --- START OF MODIFICATION (SPRINT 2.4) ---
from backend.models.scenario import ShiftValidationRequest
# --- END OF MODIFICATION (SPRINT 2.4) ---
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
    def run_scenario_prediction(self, request: ShiftValidationRequest) -> Dict: # <-- MODIFIED (S2.4)
        """
        Main orchestrator for [Task 4.c: Orchestrate API Endpoint].
        This method chains all required tasks from Sprints 2 and 3
        to generate the final savings estimate (FR4.2).
        
        MODIFIED (S2.4):
        - Accepts the full ShiftValidationRequest object.
        - Calls the new, robust validate_shift_input method.
        - Allows HTTPExceptions to bubble up to the API router.
        """
        
        # [Sprint 2: Validate Shift Input]
        # This will raise an HTTPException if invalid, halting execution
        # (fulfills NFR-S3).
        validated_device = self.validate_shift_input(request.device_id)
        
        # [Sprint 2: Create Baseline Curve]
        self.baseline_usage_curve = self.create_timestamped_curve(self.raw_usage_logs)
        
        # [Sprint 3: Calculate Baseline Cost]
        # --- MODIFIED (S3.1) ---
        # This now calls our new, robust calculation method.
        self.baseline_cost = self.calculate_total_cost(self.baseline_usage_curve)
        
        # [Sprint 3: Simulate Load Subtraction]
        temp_curve = self.simulate_load_subtraction(
            self.baseline_usage_curve, 
            validated_device, # <-- Pass the validated device 
            request.original_timestamp
        )
        
        # [Sprint 3: Simulate Load Addition]
        self.scenario_usage_curve = self.simulate_load_addition(
            temp_curve, 
            validated_device, # <-- Pass the validated device
            request.new_timestamp
        )
        
        # [Sprint 3: Calculate Scenario Cost]
        # --- MODIFIED (S3.1) ---
        # We reuse our D.R.Y. function to calculate the new cost.
        self.scenario_cost = self.calculate_total_cost(self.scenario_usage_curve)
        
        # [Task 4a: Calculate Final Savings]
        self.estimated_savings = self.calculate_final_savings(
            self.baseline_cost, 
            self.scenario_cost
        )
        
        # [Task 4b: Structure JSON Output]
        return self.structure_json_output()

    # --- Sprint 2: Retrieval Methods ---
    
    # --- START OF MODIFICATION (SPRINT 2.4) ---
    def validate_shift_input(self, device_id: int) -> Device:
        """
        Implementation for [Sprint 2: Validate Shift Input].
        
        Checks if a device exists within the engine's property context
        and is marked as 'is_shiftable'.
        
        This adheres to the "Explicit Error Handling" (P3) and
        "NFR-S3" (Failure Handling) standards by raising
        HTTPExceptions that the API router can return to the user.
        
        Args:
            device_id (int): The ID of the device to validate.
            
        Raises:
            HTTPException (404): If the device is not found.
            HTTPException (400): If the device is found but not shiftable.
            
        Returns:
            Device: The full, validated Device object if successful.
        """
        device = self._get_device_by_id(device_id)
        
        if not device:
            # Adheres to NFR-S3, as seen in Sprint 2.1 test results
            raise HTTPException(
                status_code=404,
                detail=f"Device with id {device_id} not found in this property."
            )
            
        if not device.is_shiftable:
            # Fulfills FR4.1 by checking the device rule
            raise HTTPException(
                status_code=400, # 400 Bad Request is appropriate
                detail=f"Device '{device.device_name}' is not shiftable."
            )
            
        # Success: Return the validated device for Sprint 3 logic
        return device
    # --- END OF MODIFICATION (SPRINT 2.4) ---

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
            # Use the `calculate_cost` method from the Tariff model
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
    
    # --- START OF MODIFICATION (SPRINT 3.1) ---
    def calculate_total_cost(self, usage_curve: pd.DataFrame) -> float:
        """
        Implementation for [Sprint 3.1: Calculate Baseline Cost]
        and [Sprint 3.4: Calculate Scenario Cost].
        
        This function is D.R.Y. (P1) and calculates the single total cost
        from a given usage curve DataFrame by summing its 'kwh_cost' column.
        
        It includes explicit error handling (P3, NFR-S3).
        """
        try:
            # Check if the DataFrame is empty
            if usage_curve.empty:
                logging.warning("calculate_total_cost received an empty DataFrame.")
                return 0.0
                
            # Check if the required column exists
            if "kwh_cost" not in usage_curve.columns:
                logging.error("Missing 'kwh_cost' column in usage_curve.")
                # Raise an error that our orchestrator can catch
                raise HTTPException(
                    status_code=500, 
                    detail="Internal error: Cost column missing from calculation."
                )

            # Use the built-in pandas sum() function.
            # .sum() safely returns 0.0 for an empty Series, but we check above anyway.
            total_cost = usage_curve["kwh_cost"].sum()
            
            # Return as a standard Python float
            return float(total_cost)

        except Exception as e:
            # Catch any other unexpected pandas errors
            logging.error(f"Error calculating total cost: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Internal calculation error: {e}"
            )
    # --- END OF MODIFICATION (SPRINT 3.1) ---

    # --- START OF MODIFICATION (SPRINT 3.2) ---
    def simulate_load_subtraction(self, usage_curve: pd.DataFrame, device: Device, time: datetime) -> pd.DataFrame: # <-- MODIFIED (S2.4)
        """
        Implementation for [Sprint 3.2: Simulate Load Subtraction].
        Removes a device's load from the baseline curve at a specific time.
        
        This logic is taken directly from the 'sprint3.docx' documentation.
        """
        # Adhere to NFR-S3 by creating a copy.
        # This prevents changing the original baseline curve.
        modified_curve = usage_curve.copy()
        
        try:
            # 1. Calculate the energy (kWh) to subtract.
            # As per API-info.docx, our data is half-hourly, so we multiply by 0.5.
            energy_to_subtract_kwh = device.average_draw_kW * 0.5
            
            # 2. Find the row for the specified time and subtract the energy.
            # We use .at[] for a fast, direct lookup and update.
            original_consumption = modified_curve.at[time, "kwh_consumption"]
            new_consumption = original_consumption - energy_to_subtract_kwh
            
            # Ensure consumption doesn't go below zero
            if new_consumption < 0:
                new_consumption = 0.0
                
            modified_curve.at[time, "kwh_consumption"] = new_consumption
            
            # 3. Recalculate the cost for *only* this modified row.
            new_cost = self.tariff.calculate_cost(
                kwh_consumption=new_consumption,
                timestamp=time
            )
            modified_curve.at[time, "kwh_cost"] = new_cost
            
            return modified_curve

        except KeyError:
            # This is our NFR-S3 graceful failure.
            # If the timestamp doesn't exist, log it and return the
            # original, unmodified curve.
            logging.warning(f"Timestamp {time} not found in usage curve. No subtraction performed.")
            return usage_curve
        except Exception as e:
            # P3: Catch-all for any other pandas errors
            logging.error(f"Error in simulate_load_subtraction: {e}")
            # Raise an error to stop the calculation
            raise HTTPException(
                status_code=500, 
                detail=f"Internal calculation error: {e}"
            )
    # --- END OF MODIFICATION (SPRINT 3.2) ---

    # --- START OF MODIFICATION (SPRINT 3.3) ---
    def simulate_load_addition(self, usage_curve: pd.DataFrame, device: Device, time: datetime) -> pd.DataFrame:
        """
        Implementation for [Sprint 3.3: Simulate Load Addition].
        Adds a device's load to the usage curve at a new time.
        
        This logic mirrors S3.2 (Simulate Load Subtraction).
        """
        # Adhere to NFR-S3 by creating a copy.
        # This prevents changing the intermediate curve.
        modified_curve = usage_curve.copy()

        try:
            # 1. Calculate the energy (kWh) to add.
            # As per API-info.docx, our data is half-hourly, so we multiply by 0.5.
            energy_to_add_kwh = device.average_draw_kW * 0.5
            
            # 2. Find the row for the specified time and ADD the energy.
            # We use .at[] for a fast, direct lookup and update.
            original_consumption = modified_curve.at[time, "kwh_consumption"]
            new_consumption = original_consumption + energy_to_add_kwh
            
            modified_curve.at[time, "kwh_consumption"] = new_consumption
            
            # 3. Recalculate the cost for *only* this modified row.
            new_cost = self.tariff.calculate_cost(
                kwh_consumption=new_consumption,
                timestamp=time
            )
            modified_curve.at[time, "kwh_cost"] = new_cost
            
            return modified_curve

        except KeyError:
            # This is our NFR-S3 graceful failure.
            # If the new_timestamp doesn't exist, log it and return the
            # unmodified, subtracted curve.
            logging.warning(f"Timestamp {time} not found in usage curve. No addition performed.")
            return usage_curve
        except Exception as e:
            # P3: Catch-all for any other pandas errors
            logging.error(f"Error in simulate_load_addition: {e}")
            # Raise an error to stop the calculation
            raise HTTPException(
                status_code=500, 
                detail=f"Internal calculation error: {e}"
            )
    # --- END OF MODIFICATION (SPRINT 3.3) ---

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
        # This logic is sound and supports the new validate_shift_input
        for device in self.property.devices:
            if device.device_id == device_id:
                return device
        return None