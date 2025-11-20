# This file defines the core business logic class for the system,
# as per the UML Class Diagram and Flowchart (Task 1.d: Engine Class Setup).
# All calculation logic (Sprints 2, 3, 4) will live here.

import pandas as pd
from datetime import datetime

# --- START OF MODIFICATION (SPRINT 4.2) ---
# We remove 'Dict' as we now use a Pydantic model
from typing import List, Optional

# --- END OF MODIFICATION (SPRINT 4.2) ---
from fastapi import (
    HTTPException,
)  # <-- MODIFIED (S2.4): For error handling (NFR-S3)
import logging  # <-- ADDED (S3.1): For logging errors

# Use absolute imports from 'backend' to be discoverable by pytest
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog

# --- START OF MODIFICATION (SPRINT 4.2) ---
# Import all required models for input and output
from backend.models.scenario import (
    ShiftValidationRequest,
    OptimisationReport,
    UsageDataPoint,
)

# --- END OF MODIFICATION (SPRINT 4.2) ---
# ---------------------


class OptimisationEngine:
    """
    The core intelligence class for the Green Energy Optimiser.
    This class ingests context (Property, Tariff) and data (Usage)
    and provides all calculation and recommendation logic.
    """

    def __init__(
        self,
        property_context: Property,
        tariff_context: Tariff,
        usage_data: List[HistoricalUsageLog],
    ):
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

    # --- START OF MODIFICATION (SPRINT 4.2) ---
    # The main orchestrator now returns our validated Pydantic model
    def run_scenario_prediction(
        self, request: ShiftValidationRequest
    ) -> OptimisationReport:
        # --- END OF MODIFICATION (SPRINT 4.2) ---
        """
        Main orchestrator for [Task 4.c: Orchestrate API Endpoint].
        This method chains all required tasks from Sprints 2 and 3
        to generate the final savings estimate (FR4.2).

        MODIFIED (S2.4):
        - Accepts the full ShiftValidationRequest object.
        - Calls the new, robust validate_shift_input method.
        - Allows HTTPExceptions to bubble up to the API router.

        MODIFIED (S4.2):
        - Return type is now the 'OptimisationReport' Pydantic model.
        - Calls the new 'structure_report_output' method.
        """

        try:
            # [Sprint 2: Validate Shift Input]
            # This will raise an HTTPException if invalid, halting execution
            # (fulfills NFR-S3).
            validated_device = self.validate_shift_input(request.device_id)

            # [Sprint 2: Create Baseline Curve]
            self.baseline_usage_curve = self.create_timestamped_curve(
                self.raw_usage_logs
            )

            # [Sprint 3: Calculate Baseline Cost]
            self.baseline_cost = self.calculate_total_cost(self.baseline_usage_curve)

            # [Sprint 3: Simulate Load Subtraction]
            temp_curve = self.simulate_load_subtraction(
                self.baseline_usage_curve,
                validated_device,
                request.original_timestamp,
            )

            # [Sprint 3: Simulate Load Addition]
            self.scenario_usage_curve = self.simulate_load_addition(
                temp_curve, validated_device, request.new_timestamp
            )

            # [Sprint 3: Calculate Scenario Cost]
            self.scenario_cost = self.calculate_total_cost(self.scenario_usage_curve)

            # [Task 4a: Calculate Final Savings]
            self.estimated_savings = self.calculate_final_savings(
                self.baseline_cost, self.scenario_cost
            )

            # [Task 4b: Structure JSON Output]
            # This now returns the full Pydantic model
            return self.structure_report_output()

        except HTTPException:
            # Re-raise known validation/calculation errors directly
            raise
        except Exception as e:
            # P3: Catch-all for any other unexpected errors
            logging.error(f"Critical error in run_scenario_prediction: {e}")
            # This is a generic 500 error
            raise HTTPException(
                status_code=500, detail=f"An unexpected internal error occurred: {e}"
            )

    # --- Sprint 2: Retrieval Methods ---

    def validate_shift_input(self, device_id: int) -> Device:
        """
        Implementation for [Sprint 2: Validate Shift Input].

        Checks if a device exists within the engine's property context
        and is marked as 'is_shiftable'.

        This adheres to the "Explicit Error Handling" (P3) and
        "NFR-S3" (Failure Handling) standards by raising
        HTTPExceptions that the API router can return to the user.
        """
        device = self._get_device_by_id(device_id)

        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"Device with id {device_id} not found in this property.",
            )

        if not device.is_shiftable:
            raise HTTPException(
                status_code=400,  # 400 Bad Request is appropriate
                detail=f"Device '{device.device_name}' is not shiftable.",
            )

        return device

    def create_timestamped_curve(
        self, usage_logs: List[HistoricalUsageLog]
    ) -> pd.DataFrame:
        """
        Implementation for [Sprint 2: Create Baseline Curve].

        Converts raw log data into a structured Pandas DataFrame and
        calculates the cost for each timestamp using the class's tariff.
        This fulfils the "Cost Before Scenario" requirement.
        """
        data_for_df = []

        for log in usage_logs:
            # The Tariff class (from UML) must have a 'calculate_cost' method
            calculated_cost = self.tariff.calculate_cost(
                kwh_consumption=log.kwh_consumption, timestamp=log.timestamp
            )

            data_for_df.append(
                {
                    "timestamp": log.timestamp,
                    "kwh_consumption": log.kwh_consumption,
                    "kwh_cost": calculated_cost,
                }
            )

        # --- START OF SPRINT 4.3 FIX (Timezone Mismatch) ---
        if not data_for_df:
            logging.warning("No usage logs provided to create_timestamped_curve.")
            return pd.DataFrame()  # Return empty DataFrame

        curve_df = pd.DataFrame(data_for_df)

        # 1. Convert the 'timestamp' column to be explicitly UTC-aware.
        #    This ensures it can be matched against the UTC-aware
        #    timestamps from the API request.
        try:
            curve_df["timestamp"] = pd.to_datetime(curve_df["timestamp"], utc=True)
        except Exception as e:
            logging.error(f"Error converting timestamps to UTC: {e}")
            raise HTTPException(
                status_code=500, detail="Internal error processing timestamp data."
            )

        # 2. Set the UTC-aware column as the index.
        curve_df.set_index("timestamp", inplace=True)
        # --- END OF SPRINT 4.3 FIX (Timezone Mismatch) ---

        return curve_df

    # --- Sprint 3: Calculation Methods ---

    def calculate_total_cost(self, usage_curve: pd.DataFrame) -> float:
        """
        Implementation for [Sprint 3.1: Calculate Baseline Cost]
        and [Sprint 3.4: Calculate Scenario Cost].

        This function is D.R.Y. (P1) and calculates the single total cost
        from a given usage curve DataFrame by summing its 'kwh_cost' column.

        It includes explicit error handling (P3, NFR-S3).
        """
        try:
            if usage_curve.empty:
                logging.warning("calculate_total_cost received an empty DataFrame.")
                return 0.0

            if "kwh_cost" not in usage_curve.columns:
                logging.error("Missing 'kwh_cost' column in usage_curve.")
                raise HTTPException(
                    status_code=500,
                    detail="Internal error: Cost column missing from calculation.",
                )

            total_cost = usage_curve["kwh_cost"].sum()
            return float(total_cost)

        except Exception as e:
            logging.error(f"Error calculating total cost: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal calculation error: {e}"
            )

    def simulate_load_subtraction(
        self, usage_curve: pd.DataFrame, device: Device, time: datetime
    ) -> pd.DataFrame:
        """
        Implementation for [Sprint 3.2: Simulate Load Subtraction].
        Removes a device's load from the baseline curve at a specific time.
        """
        modified_curve = usage_curve.copy()

        try:
            # 1. Calculate the energy (kWh) to subtract.
            # As per API-info.docx, our data is half-hourly (0.5 hours).
            energy_to_subtract_kwh = device.average_draw_kW * 0.5

            # 2. Find the row and subtract the energy.
            original_consumption = modified_curve.at[time, "kwh_consumption"]
            new_consumption = original_consumption - energy_to_subtract_kwh

            if new_consumption < 0:
                new_consumption = 0.0

            modified_curve.at[time, "kwh_consumption"] = new_consumption

            # 3. Recalculate the cost for *only* this modified row.
            new_cost = self.tariff.calculate_cost(
                kwh_consumption=new_consumption, timestamp=time
            )
            modified_curve.at[time, "kwh_cost"] = new_cost

            return modified_curve

        except KeyError:
            # This is the warning you saw. It's good that it's here.
            logging.warning(
                f"Timestamp {time} not found in usage curve. No subtraction performed."
            )
            return usage_curve
        except Exception as e:
            logging.error(f"Error in simulate_load_subtraction: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal calculation error: {e}"
            )

    def simulate_load_addition(
        self, usage_curve: pd.DataFrame, device: Device, time: datetime
    ) -> pd.DataFrame:
        """
        Implementation for [Sprint 3.3: Simulate Load Addition].
        Adds a device's load to the usage curve at a new time.
        """
        modified_curve = usage_curve.copy()

        try:
            # 1. Calculate the energy (kWh) to add.
            energy_to_add_kwh = device.average_draw_kW * 0.5

            # 2. Find the row and ADD the energy.
            original_consumption = modified_curve.at[time, "kwh_consumption"]
            new_consumption = original_consumption + energy_to_add_kwh

            modified_curve.at[time, "kwh_consumption"] = new_consumption

            # 3. Recalculate the cost for *only* this modified row.
            new_cost = self.tariff.calculate_cost(
                kwh_consumption=new_consumption, timestamp=time
            )
            modified_curve.at[time, "kwh_cost"] = new_cost

            return modified_curve

        except KeyError:
            # This is the warning you saw. It's good that it's here.
            logging.warning(
                f"Timestamp {time} not found in usage curve. No addition performed."
            )
            return usage_curve
        except Exception as e:
            logging.error(f"Error in simulate_load_addition: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal calculation error: {e}"
            )

    # --- Sprint 4: Deployment Methods ---

    def calculate_final_savings(self, cost_before: float, cost_after: float) -> float:
        """
        Implementation for [Task 4a: Calculate Final Savings].
        Calculates the simple difference between baseline and scenario costs.
        """
        try:
            if cost_before is None or cost_after is None:
                logging.error("calculate_final_savings received NoneType input.")
                raise HTTPException(
                    status_code=400, detail="Cost values cannot be None"
                )

            if not isinstance(cost_before, (int, float)) or not isinstance(
                cost_after, (int, float)
            ):
                logging.error("Non numeric input provided.")
                raise HTTPException(
                    status_code=400, detail="Cost values must be numeric"
                )

            # Round to 2 decimal places for currency
            savings = round(cost_before - cost_after, 2)

            # --- START OF FIX (Sprint 4.1 Test Failure) ---
            # We must set the internal state for the orchestrator to use.
            # This was missed in the previous refactor.
            self.estimated_savings = savings
            # --- END OF FIX ---

            logging.info(
                f"Calculated final savings: {savings} (before={cost_before}, after={cost_after})"
            )
            return savings

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error in calculate_final_savings: {e}")
            raise HTTPException(
                status_code=500, detail=f"Internal calculation error: {e}"
            )

    # --- START OF MODIFICATION (SPRINT 4.2) ---
    def structure_report_output(self) -> OptimisationReport:
        """
        Implementation for [Task 4b: Structure JSON Output].

        Packages the calculated metrics and the predicted usage curve
        into the final Pydantic response model (OptimisationReport).
        This method is called last in the orchestration chain.
        """
        logging.info("Structuring final optimisation report...")

        try:
            # 1. Transform the DataFrame curve into a list of models
            # This calls our new helper method
            curve_models = self._transform_curve_to_models(
                self.scenario_usage_curve
            )

            # 2. Instantiate the final Pydantic response model
            report = OptimisationReport(
                estimated_savings=self.estimated_savings,
                baseline_cost=self.baseline_cost,
                scenario_cost=self.scenario_cost,
                predicted_usage_curve=curve_models,
            )

            logging.info(
                f"Successfully structured report with {len(curve_models)} data points."
            )
            return report

        except Exception as e:
            # P3: Explicit Error Handling
            logging.error(f"Error structuring JSON output: {e}")
            # If this fails, it's a critical internal error.
            raise HTTPException(
                status_code=500, detail=f"Internal error structuring final report: {e}"
            )

    # --- END OF MODIFICATION (SPRINT 4.2) ---

    # --- Helper Methods ---

    def _get_device_by_id(self, device_id: int) -> Optional[Device]:
        """Internal helper to find a device in the property's list."""
        for device in self.property.devices:
            if device.device_id == device_id:
                return device
        return None

    # --- START OF MODIFICATION (SPRINT 4.2) ---
    def _transform_curve_to_models(
        self, usage_curve: pd.DataFrame
    ) -> List[UsageDataPoint]:
        """
        Private helper for [Task 4b] (D.R.Y. Principle P1).

        Transforms a Pandas DataFrame (with a datetime index) into a
        list of UsageDataPoint Pydantic models for the API response.

        Adheres to P3 (Explicit Error Handling).
        """

        # NFR-S3: Graceful failure check
        if usage_curve is None or usage_curve.empty:
            logging.warning(
                "_transform_curve_to_models received an empty or None curve."
            )
            return []

        try:
            data_points: List[UsageDataPoint] = []

            # Iterate over the DataFrame rows.
            # 'row' is a Series, and 'index' is the timestamp.
            for index, row in usage_curve.iterrows():
                data_points.append(
                    UsageDataPoint(
                        timestamp=index,  # The index is our timestamp
                        kwh_consumption=row["kwh_consumption"],
                        kwh_cost=row["kwh_cost"],
                    )
                )
            return data_points

        except KeyError as e:
            # P3: This catches if 'kwh_consumption' or 'kwh_cost' is missing
            logging.error(f"Missing column in DataFrame during transformation: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal error: Missing expected data column.",
            )
        except Exception as e:
            # P3: Catch-all for other pandas/Pydantic errors
            logging.error(f"Error transforming DataFrame to models: {e}")
            raise HTTPException(
                status_code=500,
                detail="Internal error: Failed to process data for response.",
            )

    # --- END OF MODIFICATION (SPRINT 4.2) ---