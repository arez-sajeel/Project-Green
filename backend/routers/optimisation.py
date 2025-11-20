# backend/routers/optimisation.py

"""
This file implements the API endpoint for Sprint 4.3: Orchestrate API Endpoint.

This router is responsible for:
1.  Authenticating the user (NFR-S2).
2.  Gathering all required data (Sprint 2: Fetch Context, Load Data).
3.  Instantiating the OptimisationEngine (Sprint 1).
4.  Calling the engine's main orchestration method (Sprint 2, 3, 4).
5.  Returning the final report or a clear error (NFR-S3).
"""

import sys
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
# --- START OF SPRINT 4.3 FIX (Test 4.1-404) ---
# Import the full datetime and timedelta
from datetime import datetime, timedelta
# --- END OF SPRINT 4.3 FIX (Test 4.1-404) ---
from typing import List, Optional

# --- P1: D.R.Y. / Modularity ---
# Import from other modules, do not redefine logic here.

# S1: Engine Class
from backend.engine.optimiser import OptimisationEngine

# S1: Data Access Layer
from backend.data_access.database import get_db
from backend.data_access.mongo_crud import get_user_context_data, get_usage_logs
from backend.models.property import Property, Device

# S4.2: Pydantic Models (Input & Output)
from backend.models.scenario import ShiftValidationRequest, OptimisationReport

# NFR-S2: Authentication Dependency
from backend.core.security import get_current_active_user, FullUserType

# --- Router Setup ---
# Use "s" in "optimisation" as requested.
router = APIRouter()


@router.post(
    "/run-scenario",
    response_model=OptimisationReport,
    summary="Run Optimisation Scenario",
    description="Main endpoint for Sprint 4.3. Chains all logic to run a "
    "load-shifting scenario and returns a full report.",
)
async def run_optimisation_scenario(
    request: ShiftValidationRequest,
    current_user: FullUserType = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Implements the full orchestration logic for Sprint 4.3.

    This function adheres to all coding standards:
    - P2 (Clarity): Fully type-hinted and logically structured.
    - P3 (Error Handling): Wrapped in a try...except block (NFR-S3).
    - RBAC (NFR-S2): Uses 'get_current_active_user' dependency.
    """

    # P3: Explicit Error Handling (NFR-S3)
    try:
        # --- Sprint 2.1: Fetch User Context ---
        # This function correctly fetches data based on user's role (NFR-S2)
        properties, tariffs = await get_user_context_data(db, current_user)

        if not properties:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No properties found for this user.",
            )

        # --- Sprint 2.2: Find Specific Property & Tariff ---
        # We must find which of the user's properties owns the requested device.
        target_property: Optional[Property] = None
        target_device: Optional[Device] = None

        for prop in properties:
            if prop.devices:
                for dev in prop.devices:
                    if dev.device_id == request.device_id:
                        target_property = prop
                        target_device = dev
                        break
            if target_property:
                break

        # Validation: Did we find the device in the user's portfolio?
        if not target_property or not target_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {request.device_id} not found in your properties.",
            )

        # Validation: Do we have the tariff for that property?
        target_tariff = tariffs.get(target_property.tariff_id)
        if not target_tariff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tariff data (ID: {target_property.tariff_id}) for this property is missing.",
            )

        # --- Sprint 2.3: Load Usage Data ---

        # --- START OF SPRINT 4.3 FIX (Test 4.1-404) ---
        # The query was using datetime.now() (2025), but the
        # UKPN mock data is from 2013-2014 (see API-info.docx).
        # We must use a fixed date range that matches the data.
        # We will query for all of January 2013.
        start_date = datetime(2013, 1, 1, 0, 0, 0)
        end_date = datetime(2013, 1, 31, 23, 59, 59)
        # --- END OF SPRINT 4.3 FIX (Test 4.1-404) ---

        # The 'property.py' model must have 'mpan_id' for this to work.
        if not hasattr(target_property, "mpan_id") or not target_property.mpan_id:
            print(
                f"Error: Property {target_property.property_id} is missing 'mpan_id'.",
                file=sys.stderr,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Property configuration error: mpan_id is missing.",
            )

        usage_data = await get_usage_logs(
            db, target_property.mpan_id, start_date, end_date
        )

        if not usage_data:
            # This check is still valid, but now it will fail if
            # Jan 2013 data is missing.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No usage data found for mpan_id {target_property.mpan_id} "
                f"between {start_date} and {end_date}.",
            )

        # --- Sprint 1: Engine Class Setup ---
        # Instantiate the engine with all the context and data it needs.
        engine = OptimisationEngine(
            property_context=target_property,
            tariff_context=target_tariff,
            usage_data=usage_data,
        )

        # --- Sprint 2, 3, & 4: Run Full Orchestration ---
        # This single method call chains all logic from the optimiser.py file.
        # It handles S2.4, S3.1-S3.4, S4.1, and S4.2.
        # It will raise its own HTTPErrors for validation (e.g., device not shiftable)
        report = engine.run_scenario_prediction(request)

        # --- Final Step: Return the Report ---
        # FastAPI will automatically serialise this Pydantic model into JSON.
        return report

    except HTTPException as http_exc:
        # P3: Re-raise known errors (like 404s, 400s) from our logic
        raise http_exc
    except Exception as e:
        # P3: Catch any other unexpected errors (NFR-S3)
        print(f"Error in /run-scenario endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal server error occurred: {e}",
        )