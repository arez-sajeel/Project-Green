# backend/routers/context.py

# This file implements the API endpoint (route) for "Fetch User Context".
# Its sole purpose is to retrieve and return the user's data context.
#
# Adheres to Modularity:
# - Authentication is handled by the `get_current_active_user` dependency.
# - Database logic is fully isolated in `data_access.mongo_crud`.
# - Response model is defined in `models.context`.

# backend/routers/context.py

import sys
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Union
from motor.motor_asyncio import AsyncIOMotorDatabase

# Correct imports (no backend.*)
from models.user import UserRole
from models.property import Homeowner, PropertyManager
from models.context import UserContextResponse
from core.security import get_current_active_user
from data_access.mongo_crud import get_user_context_data
from data_access.database import get_db

router = APIRouter()

@router.get(
    "/context",
    response_model=UserContextResponse,
    tags=["Context"],
    summary="Fetch User Context (Sprint 2)",
)
async def get_user_context(
    current_user: Union[Homeowner, PropertyManager] = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retrieves all context data for a given user
    """

    try:
        properties, tariffs = await get_user_context_data(db, current_user)

        if not properties:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No properties found for this user."
            )

        return UserContextResponse(
            user_id=str(current_user.email),
            properties=properties,
            tariffs={str(t_id): tariff for t_id, tariff in tariffs.items()}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /context: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Server error while fetching context: {e}"
        )
