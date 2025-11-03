# This file contains the unit tests for the OptimisationEngine.
# It tests the logic of the class in isolation using mock data,
# without needing a live database connection.
# All test cases are derived from 'testPlan Optomisation Engine.docx'.

import pytest
from datetime import datetime

# --- Imports updated for absolute path from root ---
from backend.engine.optimiser import OptimisationEngine
from backend.models.property import Property, Device
from backend.models.tariff import Tariff
from backend.models.usage import HistoricalUsageLog
from typing import List # Added missing import

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
            kwh_cost=60.0, # 2.0 * 30.0
            reading_type="A"
        ),
        HistoricalUsageLog(
            timestamp=datetime(2025, 1, 1, 3, 0), # 3 AM (Off-Peak)
            mpan_id="12345",
            kwh_consumption=0.5,
            kwh_cost=5.0, # 0.5 * 10.0
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

def test_validate_shift_input(engine, mock_device_shiftable, mock_device_non_shiftable):
    """
    Tests the logic for [Sprint 2: Validate Shift Input].
    
    Links to: Test Plan 2.2: test_validate_shift_input
    """
    dummy_time = datetime(2025, 1, 2, 4, 0) # 4 AM
    
    # Test 1 (Happy Path): A shiftable device should return True
    can_shift = engine.validate_shift_input(
        device_id=mock_device_shiftable.device_id,
        new_time=dummy_time
    )
    assert can_shift == True
    
    # Test 2 (Unhappy Path): A non-shiftable device should return False
    cant_shift = engine.validate_shift_input(
        device_id=mock_device_non_shiftable.device_id,
        new_time=dummy_time
    )
    assert cant_shift == False
    
    # Test 3 (Error Path): A device that doesn't exist should return False
    fake_device = engine.validate_shift_input(
        device_id=999,
        new_time=dummy_time
    )
    assert fake_device == False

def test_run_scenario_prediction_stub(engine, mock_device_shiftable):
    """
    Tests the main orchestration stub [Sprint 4: Orchestrate API Endpoint].
    This confirms the dummy values flow through the stubs correctly
    and that error handling (NFR-S3) is working.
    
    Links to: Test Plan 2.4: test_run_scenario_prediction_stub
    """
    start_time = datetime(2025, 1, 1, 18, 0) # 6 PM
    end_time = datetime(2025, 1, 2, 4, 0)   # 4 AM
    
    # Test 1 (Happy Path): Run the main orchestrator
    result = engine.run_scenario_prediction(
        device_id=mock_device_shiftable.device_id,
        original_time=start_time,
        new_time=end_time
    )
    
    # Because all our calculation stubs return 0.0, the final
    # savings should also be 0.0
    assert result["estimated_savings"] == 0.0
    
    # Test 2 (Error Path): Check that a ValueError is raised for an invalid device
    with pytest.raises(ValueError, match="Invalid shift"):
        engine.run_scenario_prediction(
            device_id=999, # Fake device
            original_time=start_time,
            new_time=end_time
        )
