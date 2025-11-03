# backend/routers/context.py

# This file implements the API endpoint (route) for "Fetch User Context".
# Its sole purpose is to retrieve and return the user's data context.
#
# Adheres to Modularity:
# - Authentication is handled by the `get_current_active_user` dependency.
# - Database logic is fully isolated in `data_access.mongo_crud`.
# - Response model is defined in `models.context`.

import sys
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union

# Import models
from backend.models.user import UserRole
from backend.models.property import Homeowner, PropertyManager
from backend.models.context import UserContextResponse

# Import auth dependency
from backend.core.security import get_current_active_user

# Import data access function
from backend.data_access.mongo_crud import get_user_context_data
from backend.data_access.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

# Create the router for this feature
router = APIRouter()

@router.get(
    "/context",
    response_model=UserContextResponse,
    tags=["Context"],
    summary="Fetch User Context (Sprint 2)",
    description="""
    Retrieves all necessary context for a user:
    - User ID
    - List of their properties (one for Homeowner, many for PropertyManager)
    - Dictionary of all associated tariffs and their rate schedules.
    
    This endpoint enforces NFR-S2 (Access Control) automatically
    based on the user's role from their JWT.
    """
)
async def get_user_context(
    # This dependency provides the user's full model (Homeowner or PropertyManager)
    current_user: Union[Homeowner, PropertyManager] = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    API endpoint to fetch the user's full operational context.
    """
    try:
        # Call the isolated data access function to get properties and tariffs
        properties, tariffs = await get_user_context_data(db, current_user)
        
        if not properties:
            # This might happen if a user is created but their property isn't
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No properties found for this user. Please complete profile setup."
            )
            
        # Package the data into the Pydantic response model
        # Note: We convert tariff_id keys to strings, as JSON keys must be strings.
        return UserContextResponse(
            user_id=str(current_user.email), # Use email as a stable user_id
            properties=properties,
            tariffs={str(t_id): tariff for t_id, tariff in tariffs.items()}
        )
        
    except HTTPException as http_exc:
        # Re-raise known HTTP exceptions
        raise http_exc
    except Exception as e:
        # Catch any unexpected errors (NFR-S3)
        print(f"Error in /context endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred while fetching user context: {e}"
        )
