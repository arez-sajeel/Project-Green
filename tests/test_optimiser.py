# This file contains the unit tests for the OptimisationEngine.
# It tests the logic of the class in isolation using mock data,
# without needing a live database connection.
# All test cases are derived from 'testPlan Optomisation Engine.docx'.

import pytest
from datetime import datetime
import pandas as pd # <-- ADDED (S3.1): For error handling test
from fastapi import HTTPException # <-- ADDED (S3.1): For error handling test

# --- Imports updated for absolute path from root ---
from backend.engine.optimiser import OptimisationEngine
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
# --- START OF MODIFICATION (Test Refactor) ---
# This import is required for the updated S2.4 test
from backend.models.scenario import ShiftValidationRequest
# --- END OF MODIFICATION (Test Refactor) ---
from typing import List # Added missing import

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

# --- START OF MODIFICATION (SPRINT 3.2) ---
# We create fixtures for our key timestamps to keep tests DRY
@pytest.fixture
def peak_time() -> datetime:
    """A mock peak time (6 PM)."""
    return datetime(2025, 1, 1, 18, 0)

@pytest.fixture
def off_peak_time() -> datetime:
    """A mock off-peak time (3 AM)."""
    return datetime(2025, 1, 1, 3, 0)
# --- END OF MODIFICATION (SPRINT 3.2) ---


@pytest.fixture
def mock_usage_logs(peak_time, off_peak_time) -> List[HistoricalUsageLog]: # Modified
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
    
    Links to: Test Plan 2.1: test_engine_initialisation
    """
    assert engine.property == mock_property
    assert engine.tariff == mock_tariff
    assert engine.raw_usage_logs == mock_usage_logs
    assert engine.property.devices[0].device_name == "Washing Machine"

def test_calculate_final_savings_stub(engine):
    """
    Tests the stub logic for [Task 4a: Calculate Final Savings].
    
    Links to: Test Plan 2.3: test_calculate_final_savings_stub
    """
    # Test the direct calculation: (Cost Before) - (Cost After)
    baseline_cost = 150.75 # Mock cost before
    scenario_cost = 110.25 # Mock cost after
    
    savings = engine.calculate_final_savings(baseline_cost, scenario_cost)
    
    # The stub logic is (baseline_cost - scenario_cost)
    assert savings == 40.50
    # Check that the engine's internal state was also set
    assert engine.estimated_savings == 40.50

# --- START OF MODIFICATION (Test Refactor) ---
def test_validate_shift_input(engine, mock_device_shiftable, mock_device_non_shiftable):
    """
    Tests the logic for [Sprint 2: Validate Shift Input].
    
    Links to: Test Plan 2.2: test_validate_shift_input
    
    REFACTORED: This test is updated to match the S2.4 implementation,
    which uses HTTPException for error handling (NFR-S3).
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

def test_run_scenario_prediction_stub(engine, mock_device_shiftable, peak_time): # Modified
    """
    Tests the main orchestration stub [Sprint 4: Orchestrate API Endpoint].
    This confirms the dummy values flow through the stubs correctly
    and that error handling (NFR-S3) is working.
    
    Links to: Test Plan 2.4: test_run_scenario_prediction_stub
    
    REFACTORED: This test is updated to match the S2.4 implementation,
    which now takes a single `ShiftValidationRequest` Pydantic model.
    """
    start_time = peak_time # Use fixture: 6 PM
    end_time = datetime(2025, 1, 2, 4, 0)   # 4 AM
    
    # Test 1 (Happy Path): Run the main orchestrator
    request = ShiftValidationRequest(
        device_id=mock_device_shiftable.device_id,
        original_timestamp=start_time,
        new_timestamp=end_time
    )
    result = engine.run_scenario_prediction(request)
    
    # --- MODIFIED (S3.2) ---
    # We now have S3.2 (Subtraction) implemented.
    # Baseline Cost = 65.0
    # Scenario Cost = 37.5 (peak) + 5.0 (off-peak) = 42.5
    # Savings = 65.0 - 42.5 = 22.5
    # The 'simulate_load_addition' stub still just returns the curve
    # it was given, so this calculation is now correct.
    assert result["baseline_cost"] == 65.0
    assert result["scenario_cost"] == 42.5
    assert result["estimated_savings"] == 22.5
    
    # Test 2 (Error Path): Check that an HTTPException is raised
    # This comes from the `validate_shift_input` step failing.
    with pytest.raises(HTTPException) as e:
        invalid_request = ShiftValidationRequest(
            device_id=999, # Fake device
            original_timestamp=start_time,
            new_timestamp=end_time
        )
        engine.run_scenario_prediction(invalid_request)
    
    assert e.value.status_code == 404 # 404 Not Found
# --- END OF MODIFICATION (Test Refactor) ---


# --- Test from Sprint 2.c (Unchanged) ---
def test_create_timestamped_curve(engine, mock_usage_logs):
    """
    Tests the implementation for [Sprint 2: Create Baseline Curve].
    
    This test validates that the `create_timestamped_curve` method
    correctly loops through raw logs and uses the `Tariff.calculate_cost`
    method (tested in Step 1) to build the baseline cost curve.
    
    Links to: Test Plan 2.5: test_create_timestamped_curve
    """
    # GIVEN: The 'engine' fixture, which has a mock tariff and
    # two mock usage logs (one peak, one off-peak).
    
    # WHEN: We call the method to create the baseline curve
    baseline_curve_df = engine.create_timestamped_curve(mock_usage_logs)
    
    # THEN: The DataFrame should be correctly calculated.
    
    # 1. Check the DataFrame isn't empty
    assert not baseline_curve_df.empty
    
    # 2. Check that our new cost column exists
    assert "kwh_cost" in baseline_curve_df.columns
    
    # 3. Check the calculated costs are correct based on our fixtures:
    #    Log 1 (Peak): 2.0 kWh * 30.0p/kWh = 60.0
    #    Log 2 (Off-Peak): 0.5 kWh * 10.0p/kWh = 5.0
    expected_costs = [60.0, 5.0]
    
    # We use .tolist() to compare the values inside the Pandas Series
    assert baseline_curve_df["kwh_cost"].tolist() == expected_costs

# --- START OF NEW TESTS (SPRINT 3.1) ---

def test_calculate_total_cost_happy_path(engine):
    """
    Tests the implementation for [Sprint 3.1: Calculate Baseline Cost].
    
    This test validates that the `calculate_total_cost` method
    correctly sums the 'kwh_cost' column of a given DataFrame.
    
    Links to: Test Plan 3.1: test_calculate_baseline_cost (New)
    """
    # GIVEN:
    # 1. A valid baseline curve, which we get from our S2.c method.
    #    We know from the test above this curve has costs [60.0, 5.0].
    baseline_curve = engine.create_timestamped_curve(engine.raw_usage_logs)
    
    # WHEN:
    # We call our new method to calculate the total cost.
    total_cost = engine.calculate_total_cost(baseline_curve)
    
    # THEN:
    # The total cost should be the sum of the column.
    assert total_cost == 65.0

def test_calculate_total_cost_error_handling(engine):
    """
    Tests the error handling for [Sprint 3.1] (P3 / NFR-S3).
    
    This test ensures the function fails gracefully if the data
    is missing or malformed.
    """
    # Test 1 (NFR-S3): Empty DataFrame
    # GIVEN: An empty DataFrame
    empty_df = pd.DataFrame()
    # WHEN: We call the method
    total_cost_empty = engine.calculate_total_cost(empty_df)
    # THEN: It should safely return 0.0
    assert total_cost_empty == 0.0
    
    # Test 2 (P3): Missing 'kwh_cost' column
    # GIVEN: A DataFrame with the wrong column name
    bad_df_data = [{"timestamp": datetime(2025, 1, 1, 1, 0), "wrong_column": 50.0}]
    bad_df = pd.DataFrame(bad_df_data).set_index("timestamp")
    
    # WHEN/THEN: It should raise an HTTPException, as per our standard
    with pytest.raises(HTTPException) as e:
        engine.calculate_total_cost(bad_df)
    
    # Check that it's the 500 error we expect
    assert e.value.status_code == 500
    assert "Cost column missing" in e.value.detail

# --- END OF NEW TESTS (SPRINT 3.1) ---


# --- START OF NEW TEST (SPRINT 3.2) ---
# --- MODIFICATION (Test Refactor) ---
# This test is updated to pass the full `Device` object, not the `device_id`.
# This is based on the `sprint3.docx` stating S3.2 passed, implying
# the `optimiser.py` stub (which takes `device: Device`) is correct.
def test_simulate_load_subtraction(engine, mock_device_shiftable, peak_time, off_peak_time):
    """
    Tests the implementation for [Sprint 3: Simulate Load Subtraction].
    
    This test validates that the method correctly subtracts a device's
    load from a single timestamp and recalculates the cost for that row.
    
    Links to: Test Plan 3.2: test_simulate_load_subtraction (New)
    """
    # GIVEN:
    # 1. The baseline curve (which we know is correct from the test above)
    baseline_curve = engine.create_timestamped_curve(engine.raw_usage_logs)
    # 2. The mock shiftable device (1.5 kW)
    # 3. The peak timestamp (6 PM)
    
    # WHEN:
    # We simulate subtracting the device's load from the peak time
    subtracted_curve = engine.simulate_load_subtraction(
        usage_curve=baseline_curve,
        device=mock_device_shiftable, # <-- PASS THE FULL OBJECT
        time=peak_time
    )
    
    # THEN:
    # 1. Calculate the expected new values for the PEAK time
    # Energy to subtract = 1.5 kW * 0.5 h = 0.75 kWh
    # New Consumption = 2.0 kWh (original) - 0.75 kWh = 1.25 kWh
    # New Cost = 1.25 kWh * 30.0p/kWh (peak rate) = 37.5
    
    # 2. Check the PEAK row (6 PM)
    peak_row = subtracted_curve.loc[peak_time]
    assert peak_row['kwh_consumption'] == 1.25
    assert peak_row['kwh_cost'] == 37.5
    
    # 3. Check the OFF-PEAK row (3 AM) to ensure it was NOT changed
    off_peak_row = subtracted_curve.loc[off_peak_time]
    assert off_peak_row['kwh_consumption'] == 0.5 # Unchanged from original
    assert off_peak_row['kwh_cost'] == 5.0     # Unchanged from original

# --- END OF NEW TEST ---

