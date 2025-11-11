# This file contains the unit tests for the OptimisationEngine.
# It tests the logic of the class in isolation using mock data,
# without needing a live database connection.
# All test cases are derived from 'testPlan Optomisation Engine.docx'.

import pytest
from datetime import datetime
import pandas as pd
from fastapi import HTTPException

# --- Imports updated for absolute path from root ---
from backend.engine.optimiser import OptimisationEngine
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
from typing import List # Added missing import

# --- START OF MODIFICATION (SPRINT 4.2) ---
# Import all required models for input and output
from backend.models.scenario import (
    ShiftValidationRequest,
    OptimisationReport,
    UsageDataPoint
)
# --- END OF MODIFICATION (SPRINT 4.2) ---


# --- Mock Data Setup (Fixtures) ---
# These fixtures provide mock data as defined in the Test Strategy (Test Plan 1.0)

@pytest.fixture
def mock_device_shiftable() -> Device:
    """A mock device that is shiftable (FR4.1)."""
    return Device(
        device_id=1,
        device_name="Washing Machine",
        average_draw_kW=1.5, # 1.5 kW
        is_shiftable=True
    )

@pytest.fixture
def mock_device_non_shiftable() -> Device:
    """A mock device that is NOT shiftable."""
    return Device(
        device_id=2,
        device_name="Oven",
        average_draw_kW=3.0,
        is_shiftable=False
    )

@pytest.fixture
def mock_property(mock_device_shiftable, mock_device_non_shiftable) -> Property:
    """A mock property (FR1.3) containing our test devices."""
    return Property(
        property_id=101,
        address="123 Test Street",
        location="London",
        sq_footage=1000,
        tariff_id=201,
        devices=[mock_device_shiftable, mock_device_non_shiftable]
    )

@pytest.fixture
def mock_tariff() -> Tariff:
    """A mock Time-of-Use tariff (FR1.2)."""
    return Tariff(
        tariff_id=201,
        provider_name="Test Energy",
        payment_type="Direct Debit",
        region="London",
        standing_charge_pd=50.0,
        carbon_score=80,
        rate_schedule={
            "peak": 30.0,    # 30p / kWh
            "off_peak": 10.0 # 10p / kWh
        }
    )

@pytest.fixture
def peak_time() -> datetime:
    """A mock peak time (6 PM)."""
    return datetime(2025, 1, 1, 18, 0)

@pytest.fixture
def off_peak_time() -> datetime:
    """A mock off-peak time (3 AM)."""
    return datetime(2025, 1, 1, 3, 0)


@pytest.fixture
def mock_usage_logs(peak_time, off_peak_time) -> List[HistoricalUsageLog]:
    """A list of mock usage logs (FR2.5)."""
    return [
        HistoricalUsageLog(
            timestamp=peak_time, # Use fixture: 6 PM (Peak)
            mpan_id="12345",
            kwh_consumption=2.0,
            kwh_cost=0.0, # Original cost is 0.0, to be calculated
            reading_type="A"
        ),
        HistoricalUsageLog(
            timestamp=off_peak_time, # Use fixture: 3 AM (Off-Peak)
            mpan_id="12345",
            kwh_consumption=0.5,
            kwh_cost=0.0, # Original cost is 0.0, to be calculated
            reading_type="A"
        )
    ]

@pytest.fixture
def engine(mock_property, mock_tariff, mock_usage_logs) -> OptimisationEngine:
    """A fully initialised OptimisationEngine instance for testing."""
    return OptimisationEngine(
        property_context=mock_property,
        tariff_context=mock_tariff,
        usage_data=mock_usage_logs
    )

# --- Unit Tests ---

def test_engine_initialisation(engine, mock_property, mock_tariff, mock_usage_logs):
    """
    Tests that the engine class initialises correctly.
    (Task 4.a: Engine Class Setup)
    """
    assert engine.property == mock_property
    assert engine.tariff == mock_tariff
    assert engine.raw_usage_logs == mock_usage_logs
    assert engine.property.devices[0].device_name == "Washing Machine"


def test_validate_shift_input(engine, mock_device_shiftable, mock_device_non_shiftable):
    """
    Tests the logic for [Sprint 2: Validate Shift Input].
    (NFR-S3).
    """
    
    # Test 1 (Happy Path): A shiftable device should return the Device object
    device = engine.validate_shift_input(
        device_id=mock_device_shiftable.device_id
    )
    assert device == mock_device_shiftable
    
    # Test 2 (Unhappy Path): A non-shiftable device should raise 400
    with pytest.raises(HTTPException) as e:
        engine.validate_shift_input(
            device_id=mock_device_non_shiftable.device_id
        )
    assert e.value.status_code == 400
    assert "not shiftable" in e.value.detail
    
    # Test 3 (Error Path): A device that doesn't exist should raise 404
    with pytest.raises(HTTPException) as e:
        engine.validate_shift_input(
            device_id=999
        )
    assert e.value.status_code == 404
    assert "not found" in e.value.detail

# --- START OF MODIFICATION (SPRINT 4.2) ---
def test_run_scenario_prediction(engine, mock_device_shiftable, peak_time, off_peak_time):
    """
    Tests the main orchestration [Sprint 4: Orchestrate API Endpoint].
    This confirms the full calculation chain runs and returns the
    correct Pydantic model (FR4.2).
    
    REFACTORED (S4.2): This test is updated to check for the
    'OptimisationReport' Pydantic model, not a dictionary.
    """
    
    # Test 1 (Happy Path): Run the main orchestrator
    request = ShiftValidationRequest(
        device_id=mock_device_shiftable.device_id,
        original_timestamp=peak_time,
        new_timestamp=off_peak_time
    )
    result = engine.run_scenario_prediction(request)
    
    # --- Assertions ---
    
    # 1. Check the return type is our new Pydantic model
    assert isinstance(result, OptimisationReport)
    
    # 2. Check the calculated values (from S3.3 test)
    # Baseline Cost (S3.1) = 65.0 (from 60.0 + 5.0)
    # Scenario Cost (S3.4) = 50.0 (from 37.5 + 12.5)
    # Final Savings (S4.a) = 65.0 - 50.0 = 15.0
    
    assert result.baseline_cost == 65.0
    assert result.scenario_cost == 50.0
    assert result.estimated_savings == 15.0
    
    # 3. Check the predicted usage curve (Task 4b)
    assert isinstance(result.predicted_usage_curve, list)
    assert len(result.predicted_usage_curve) == 2 # We had 2 logs
    assert isinstance(result.predicted_usage_curve[0], UsageDataPoint)
    
    # 4. Check the data *inside* the curve
    # The curve should match the 'added_curve' from S3.3 test
    # Peak time row (subtracted):
    assert result.predicted_usage_curve[0].timestamp == peak_time
    assert result.predicted_usage_curve[0].kwh_consumption == 1.25
    assert result.predicted_usage_curve[0].kwh_cost == 37.5
    # Off-peak time row (added):
    assert result.predicted_usage_curve[1].timestamp == off_peak_time
    assert result.predicted_usage_curve[1].kwh_consumption == 1.25
    assert result.predicted_usage_curve[1].kwh_cost == 12.5
    
    
    # Test 2 (Error Path): Check that an HTTPException is raised
    # This comes from the `validate_shift_input` step failing.
    with pytest.raises(HTTPException) as e:
        invalid_request = ShiftValidationRequest(
            device_id=999, # Fake device
            original_timestamp=peak_time,
            new_timestamp=off_peak_time
        )
        engine.run_scenario_prediction(invalid_request)
    
    assert e.value.status_code == 404 # 404 Not Found
# --- END OF MODIFICATION (SPRINT 4.2) ---


# --- Test from Sprint 2.c (Unchanged) ---
def test_create_timestamped_curve(engine, mock_usage_logs):
    """
    Tests the implementation for [Sprint 2: Create Baseline Curve].
    """
    # GIVEN: The 'engine' fixture
    
    # WHEN: We call the method to create the baseline curve
    baseline_curve_df = engine.create_timestamped_curve(mock_usage_logs)
    
    # THEN: The DataFrame should be correctly calculated.
    assert not baseline_curve_df.empty
    assert "kwh_cost" in baseline_curve_df.columns
    
    #    Log 1 (Peak): 2.0 kWh * 30.0p/kWh = 60.0
    #    Log 2 (Off-Peak): 0.5 kWh * 10.0p/kWh = 5.0
    expected_costs = [60.0, 5.0]
    assert baseline_curve_df["kwh_cost"].tolist() == expected_costs

# --- Tests from Sprint 3.1 ---
def test_calculate_total_cost_happy_path(engine):
    """
    Tests the implementation for [Sprint 3.1: Calculate Baseline Cost].
    """
    # GIVEN: A valid baseline curve
    baseline_curve = engine.create_timestamped_curve(engine.raw_usage_logs)
    
    # WHEN: We call our new method to calculate the total cost.
    total_cost = engine.calculate_total_cost(baseline_curve)
    
    # THEN: The total cost should be the sum of the column.
    assert total_cost == 65.0

def test_calculate_total_cost_error_handling(engine):
    """
    Tests the error handling for [Sprint 3.1] (P3 / NFR-S3).
    """
    # Test 1 (NFR-S3): Empty DataFrame
    empty_df = pd.DataFrame()
    total_cost_empty = engine.calculate_total_cost(empty_df)
    assert total_cost_empty == 0.0
    
    # Test 2 (P3): Missing 'kwh_cost' column
    bad_df_data = [{"timestamp": datetime(2025, 1, 1, 1, 0), "wrong_column": 50.0}]
    bad_df = pd.DataFrame(bad_df_data).set_index("timestamp")
    
    with pytest.raises(HTTPException) as e:
        engine.calculate_total_cost(bad_df)
    
    assert e.value.status_code == 500
    assert "Cost column missing" in e.value.detail

# --- Test from Sprint 3.2 ---
def test_simulate_load_subtraction(engine, mock_device_shiftable, peak_time, off_peak_time):
    """
    Tests the implementation for [Sprint 3: Simulate Load Subtraction].
    """
    # GIVEN: The baseline curve, device, and peak time
    baseline_curve = engine.create_timestamped_curve(engine.raw_usage_logs)
    
    # WHEN: We simulate subtracting the device's load from the peak time
    subtracted_curve = engine.simulate_load_subtraction(
        usage_curve=baseline_curve,
        device=mock_device_shiftable,
        time=peak_time
    )
    
    # THEN:
    # New Consumption = 2.0 kWh - (1.5 kW * 0.5 h) = 1.25 kWh
    # New Cost = 1.25 kWh * 30.0p/kWh = 37.5
    peak_row = subtracted_curve.loc[peak_time]
    assert peak_row['kwh_consumption'] == 1.25
    assert peak_row['kwh_cost'] == 37.5
    
    # Check the OFF-PEAK row to ensure it was NOT changed
    off_peak_row = subtracted_curve.loc[off_peak_time]
    assert off_peak_row['kwh_consumption'] == 0.5
    assert off_peak_row['kwh_cost'] == 5.0

# --- Test from Sprint 3.3 ---
def test_simulate_load_addition(engine, mock_device_shiftable, peak_time, off_peak_time):
    """
    Tests the implementation for [Sprint 3.3: Simulate Load Addition].
    """
    # GIVEN: The baseline curve and the subtracted curve
    baseline_curve = engine.create_timestamped_curve(engine.raw_usage_logs)
    subtracted_curve = engine.simulate_load_subtraction(
        usage_curve=baseline_curve,
        device=mock_device_shiftable,
        time=peak_time
    )
    
    # WHEN: We simulate adding the device's load to the OFF-PEAK time
    added_curve = engine.simulate_load_addition(
        usage_curve=subtracted_curve, # Use the subtracted curve
        device=mock_device_shiftable,
        time=off_peak_time
    )
    
    # THEN:
    # New Consumption = 0.5 kWh + (1.5 kW * 0.5 h) = 1.25 kWh
    # New Cost = 1.25 kWh * 10.0p/kWh = 12.5
    off_peak_row = added_curve.loc[off_peak_time]
    assert off_peak_row['kwh_consumption'] == 1.25
    assert off_peak_row['kwh_cost'] == 12.5
    
    # Check the PEAK row to ensure it was NOT changed
    peak_row = added_curve.loc[peak_time]
    assert peak_row['kwh_consumption'] == 1.25
    assert peak_row['kwh_cost'] == 37.5

# --- Tests from Sprint 4.1 ---
def test_calculate_final_savings_happy_path(engine):
    """
    Test the happy path for 4.1
    """
    savings = engine.calculate_final_savings(200.50, 150.25)
    assert savings == 50.25
    assert engine.estimated_savings == 50.25

def test_calculate_final_savings_negative_result(engine):
    """
    Validates correct calculation for a negative saving (a loss).
    """
    savings = engine.calculate_final_savings(100.0, 130.0)
    assert savings == -30.0
    assert engine.estimated_savings == -30.0

def test_calculate_final_savings_none_input(engine):
    """
    Validates NFR-S3 error handling for None input.
    """
    with pytest.raises(HTTPException) as e:
        engine.calculate_final_savings(None, 120.0)
    assert e.value.status_code == 400
    assert "cannot be None" in e.value.detail

def test_calculate_final_savings_invalid_type(engine):
    """
    Validates P3 error handling for non-numeric input.
    """
    with pytest.raises(HTTPException) as e:
        engine.calculate_final_savings("invalid", 120.0)
    assert e.value.status_code == 400
    assert "must be numeric" in e.value.detail

# --- START OF NEW TESTS (SPRINT 4.2) ---

def test_transform_curve_to_models_happy_path(engine, peak_time, off_peak_time):
    """
    Tests the private helper [Task 4b] to ensure it correctly
    transforms a DataFrame into a list of Pydantic models.
    """
    # GIVEN: A valid DataFrame (we'll use the scenario_curve)
    engine.run_scenario_prediction(
        ShiftValidationRequest(
            device_id=1,
            original_timestamp=peak_time,
            new_timestamp=off_peak_time
        )
    )
    scenario_curve_df = engine.scenario_usage_curve
    
    # WHEN: We call the transform method
    model_list = engine._transform_curve_to_models(scenario_curve_df)
    
    # THEN:
    assert isinstance(model_list, list)
    assert len(model_list) == 2
    assert isinstance(model_list[0], UsageDataPoint)
    
    # Check data integrity
    assert model_list[0].timestamp == peak_time
    assert model_list[0].kwh_consumption == 1.25
    assert model_list[0].kwh_cost == 37.5
    
    assert model_list[1].timestamp == off_peak_time
    assert model_list[1].kwh_consumption == 1.25
    assert model_list[1].kwh_cost == 12.5

def test_transform_curve_to_models_error_handling(engine):
    """
    Tests the NFR-S3 and P3 error handling for the transform helper.
    """
    # Test 1 (NFR-S3): Empty DataFrame
    empty_df = pd.DataFrame()
    result_empty = engine._transform_curve_to_models(empty_df)
    assert result_empty == []
    
    # Test 2 (NFR-S3): None input
    result_none = engine._transform_curve_to_models(None)
    assert result_none == []
    
    # Test 3 (P3): Missing 'kwh_cost' column
    bad_df_data = [{"timestamp": datetime(2025, 1, 1, 1, 0), "kwh_consumption": 50.0}]
    bad_df = pd.DataFrame(bad_df_data).set_index("timestamp")
    
    with pytest.raises(HTTPException) as e:
        engine._transform_curve_to_models(bad_df)
    
    assert e.value.status_code == 500
    assert "Missing expected data column" in e.value.detail

def test_structure_report_output_happy_path(engine, peak_time, off_peak_time):
    """
    Tests the [Task 4b] structuring method in isolation.
    """
    # GIVEN: Manually set the engine's state
    engine.run_scenario_prediction(
        ShiftValidationRequest(
            device_id=1,
            original_timestamp=peak_time,
            new_timestamp=off_peak_time
        )
    )
    # The orchestrator above sets all internal states:
    # engine.estimated_savings = 15.0
    # engine.baseline_cost = 65.0
    # engine.scenario_cost = 50.0
    # engine.scenario_usage_curve = (DataFrame)
    
    # WHEN: We call the structuring method
    report = engine.structure_report_output()
    
    # THEN: The report should be a valid Pydantic model
    assert isinstance(report, OptimisationReport)
    assert report.estimated_savings == 15.0
    assert report.baseline_cost == 65.0
    assert report.scenario_cost == 50.0
    assert len(report.predicted_usage_curve) == 2
    assert report.predicted_usage_curve[0].kwh_cost == 37.5

# --- END OF NEW TESTS (SPRINT 4.2) ---