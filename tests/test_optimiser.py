# This file contains the unit tests for the OptimisationEngine.
# It tests the logic of the class in isolation using mock data,
# without needing a live database connection.
# All test cases are derived from 'testPlan Optomisation Engine.docx'.

import pytest
from datetime import datetime
from fastapi import HTTPException # <-- MODIFIED (S2.4): For testing errors

# --- Imports updated for absolute path from root ---
from backend.engine.optimiser import OptimisationEngine
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
from typing import List
# --- START OF MODIFICATION (SPRINT 2.4) ---
from backend.models.scenario import ShiftValidationRequest
# --- END OF MODIFICATION (SPRINT 2.4) ---

# --- Mock Data Setup (Fixtures) ---
# These fixtures provide mock data as defined in the Test Strategy (Test Plan 1.0)

@pytest.fixture
def mock_device_shiftable() -> Device:
    """A mock device that is shiftable (FR4.1)."""
    return Device(
        device_id=1,
        device_name="Washing Machine",
        average_draw_kW=1.5,
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
def mock_usage_logs() -> List[HistoricalUsageLog]:
    """A list of mock usage logs (FR2.5)."""
    return [
        HistoricalUsageLog(
            timestamp=datetime(2025, 1, 1, 18, 0), # 6 PM (Peak)
            mpan_id="12345",
            kwh_consumption=2.0,
            kwh_cost=0.0, # Original cost is 0.0, to be calculated
            reading_type="A"
        ),
        HistoricalUsageLog(
            timestamp=datetime(2025, 1, 1, 3, 0), # 3 AM (Off-Peak)
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

# --- START OF MODIFICATION (SPRINT 2.4) ---
@pytest.fixture
def mock_shift_request(mock_device_shiftable) -> ShiftValidationRequest:
    """A mock scenario request for the shiftable device."""
    return ShiftValidationRequest(
        device_id=mock_device_shiftable.device_id,
        original_timestamp=datetime(2025, 1, 1, 18, 0), # 6 PM (Peak)
        new_timestamp=datetime(2025, 1, 2, 4, 0)      # 4 AM (Off-peak)
    )

@pytest.fixture
def mock_shift_request_invalid_device() -> ShiftValidationRequest:
    """A mock scenario request for a device that doesn't exist."""
    return ShiftValidationRequest(
        device_id=999, # Fake device
        original_timestamp=datetime(2025, 1, 1, 18, 0),
        new_timestamp=datetime(2025, 1, 2, 4, 0)
    )
# --- END OF MODIFICATION (SPRINT 2.4) ---


# --- Unit Tests ---

def test_engine_initialisation(engine, mock_property, mock_tariff, mock_usage_logs):
    """
    Tests that the engine class initialises correctly.
    (Task 1.d: Engine Class Setup)
    
    Links to: Test Plan 2.1: test_engine_initialisation
    """
    assert engine.property == mock_property
    assert engine.tariff == mock_tariff
    assert engine.raw_usage_logs == mock_usage_logs
    assert engine.property.devices[0].device_name == "Washing Machine"

def test_calculate_final_savings_stub(engine):
    """
    Tests the logic for [Task 4a: Calculate Final Savings].
    
    Links to: Test Plan 2.3: test_calculate_final_savings_stub
    """
    # Test the direct calculation: (Cost Before) - (Cost After)
    baseline_cost = 150.75 # Mock cost before
    scenario_cost = 110.25 # Mock cost after
    
    savings = engine.calculate_final_savings(baseline_cost, scenario_cost)
    
    # The logic is (baseline_cost - scenario_cost)
    assert savings == 40.50
    # Check that the engine's internal state was also set
    assert engine.estimated_savings == 40.50

# --- START OF MODIFICATION (SPRINT 2.4) ---
def test_validate_shift_input(engine, mock_device_shiftable, mock_device_non_shiftable):
    """
    Tests the logic for [Sprint 2: Validate Shift Input].
    
    Links to: Test Plan 2.2: test_validate_shift_input
    
    MODIFIED (S2.4):
    - Tests the new implementation which returns a Device
      object or raises an HTTPException (NFR-S3).
    """
    
    # Test 1 (Happy Path): A shiftable device should return the Device object
    validated_device = engine.validate_shift_input(
        device_id=mock_device_shiftable.device_id
    )
    assert validated_device == mock_device_shiftable
    
    # Test 2 (Unhappy Path): A non-shiftable device should raise 400
    with pytest.raises(HTTPException) as e:
        engine.validate_shift_input(
            device_id=mock_device_non_shiftable.device_id
        )
    assert e.value.status_code == 400
    assert "not shiftable" in e.value.detail
    
    # Test 3 (Error Path): A device that doesn't exist should raise 404
    with pytest.raises(HTTPException) as e:
        engine.validate_shift_input(device_id=999)
    assert e.value.status_code == 404
    assert "not found" in e.value.detail

def test_run_scenario_prediction_stub(engine, mock_shift_request, mock_shift_request_invalid_device):
    """
    Tests the main orchestration stub [Sprint 4: Orchestrate API Endpoint].
    
    Links to: Test Plan 2.4: test_run_scenario_prediction_stub
    
    MODIFIED (S2.4):
    - Passes the new ShiftValidationRequest model.
    - Confirms that HTTPExceptions from validation bubble up (NFR-S3).
    """
    
    # Test 1 (Happy Path): Run the main orchestrator
    result = engine.run_scenario_prediction(
        request=mock_shift_request
    )
    
    # Because all our calculation stubs return 0.0, the final
    # savings should also be 0.0
    assert result["estimated_savings"] == 0.0
    
    # Test 2 (Error Path): Check that an HTTPException is raised
    # for an invalid device.
    with pytest.raises(HTTPException) as e:
        engine.run_scenario_prediction(
            request=mock_shift_request_invalid_device
        )
    # Check that the exception from validate_shift_input bubbles up
    assert e.value.status_code == 404
# --- END OF MODIFICATION (SPRINT 2.4) ---


# --- Test from Sprint 2.c (Unchanged) ---

def test_create_timestamped_curve(engine, mock_usage_logs):
    """
    Tests the implementation for [Sprint 2: Create Baseline Curve].
    
    This test validates that the `create_timestamped_curve` method
    correctly loops through raw logs and uses the `Tariff.calculate_cost`
    method to build the baseline cost curve.
    
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
