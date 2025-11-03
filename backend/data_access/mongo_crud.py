# This file implements the base drivers for MongoDB access for all
# domain models *except* User (which is handled in database.py).
# This adheres to the "Modularity (Data Access Layer)" coding standard.
# All functions are async and include explicit error handling (NFR-S3).
# ---
# MODIFIED FOR SPRINT 2 (Fetch User Context):
# - Added `get_user_context_data` function.
# - This new function orchestrates all DB queries needed for the
#   /context/ endpoint, enforcing NFR-S2 (Access Control).
# ---

import sys
from datetime import datetime
from typing import List, Optional, Union, Dict, Set, Tuple
import typing  # Required for 'typing.cast'
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from starlette import status

# Use absolute imports
from backend.models.tariff import Tariff
from backend.models.property import Property, Device, Homeowner, PropertyManager
from backend.models.usage import HistoricalUsageLog
from backend.models.user import UserRole

# Define a type hint for the full user models
FullUserType = Union[Homeowner, PropertyManager]

# --- NEW (Sprint 2): Context Retrieval (Task: Fetch User Context) ---

async def get_user_context_data(
    db: AsyncIOMotorDatabase, user: FullUserType
) -> Tuple[List[Property], Dict[int, Tariff]]:
    """
    Fetches all properties and associated tariffs for a given user.
    This function enforces NFR-S2 (Role-Based Access Control)
    by using the user's role to determine which properties to fetch.
    
    Returns:
        A tuple containing:
        1. A list of `Property` objects.
        2. A dictionary of `Tariff` objects, keyed by tariff_id.
    """
    properties: List[Property] = []
    tariff_ids: Set[int] = set()
    tariffs: Dict[int, Tariff] = {}

    try:
        # Step 1: Fetch Properties based on User Role (NFR-S2)
        if user.role == UserRole.HOMEOWNER:
            user = typing.cast(Homeowner, user) 
            prop_doc = await db["properties"].find_one({"property_id": user.property_id})
            if prop_doc:
                prop = Property(**prop_doc)
                if prop.devices is None:
                    prop.devices = []
                properties.append(prop)
            else:
                print(f"Warning: Homeowner {user.email} links to missing property {user.property_id}", file=sys.stderr)


        elif user.role == UserRole.PROPERTY_MANAGER:
            user = typing.cast(PropertyManager, user)
            cursor = db["properties"].find({"portfolio_id": user.portfolio_id})
            async for prop_doc in cursor:
                prop = Property(**prop_doc)
                if prop.devices is None:
                    prop.devices = []
                properties.append(prop)
        
        # This handles Test Case 1.4
        if not properties:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No properties found for this user. Please complete profile setup."
            )
            
        # Step 2: Collect all unique Tariff IDs from the fetched properties
        for prop in properties:
            tariff_ids.add(prop.tariff_id)
            
        # Step 3: Fetch all unique Tariff documents
        for t_id in tariff_ids:
            tariff_doc = await get_tariff_by_id(db, t_id)
            if tariff_doc:
                tariffs[t_id] = tariff_doc
            else:
                # Data integrity issue
                print(f"Warning: Property references missing tariff_id {t_id}", file=sys.stderr)
                
        return properties, tariffs

    except PyMongoError as e:
        print(f"Error fetching user context data for {user.email}: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred."
        )
    except HTTPException as http_exc:
        # Re-raise our own 404 exception
        raise http_exc
    except Exception as e:
        print(f"Unexpected error in get_user_context_data: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {e}"
        )


# --- Tariff Collection Drivers (FR1.2, FR4.3) ---

async def add_tariff(db: AsyncIOMotorDatabase, tariff_data: Tariff) -> Optional[Tariff]:
    """
    Inserts a single new tariff document into the 'tariffs' collection.
    Used for populating the mock tariff database.
    """
    try:
        # Pydantic model_dump() converts the object to a dict
        await db["tariffs"].insert_one(tariff_data.model_dump())
        return tariff_data
    except PyMongoError as e:
        print(f"Error adding tariff: {e}", file=sys.stderr)
        return None

async def get_tariff_by_id(db: AsyncIOMotorDatabase, tariff_id: int) -> Optional[Tariff]:
    """
    Retrieves a single tariff by its tariff_id.
    Essential for calculation logic (Sprints 2 & 3).
    """
    try:
        tariff_doc = await db["tariffs"].find_one({"tariff_id": tariff_id})
        if tariff_doc:
            return Tariff(**tariff_doc)
        return None
    except PyMongoError as e:
        print(f"Error retrieving tariff {tariff_id}: {e}", file=sys.stderr)
        return None

# --- Property & Device Collection Drivers (FR1.3, FR2.4) ---

async def create_property(db: AsyncIOMotorDatabase, property_data: Property) -> Optional[Property]:
    """
    Inserts a single new property document into the 'properties' collection.
    """
    try:
        await db["properties"].insert_one(property_data.model_dump())
        return property_data
    except PyMongoError as e:
        print(f"Error creating property: {e}", file=sys.stderr)
        return None

async def get_property_by_id(db: AsyncIOMotorDatabase, property_id: int) -> Optional[Property]:
    """
    Retrieves a single property by its property_id.
    """
    try:
        property_doc = await db["properties"].find_one({"property_id": property_id})
        if property_doc:
            return Property(**property_doc)
        return None
    except PyMongoError as e:
        print(f"Error retrieving property {property_id}: {e}", file=sys.stderr)
        return None

async def add_device_to_property(db: AsyncIOMotorDatabase, property_id: int, device_data: Device) -> Optional[Property]:
    """
    Adds a new Device to a Property's embedded 'devices' list.
    Demonstrates handling of embedded documents (UML 1:* composition).
    """
    try:
        # Use $push to add the new device to the array
        update_result = await db["properties"].update_one(
            {"property_id": property_id},
            {"$push": {"devices": device_data.model_dump()}}
        )
        if update_result.modified_count == 1:
            # Return the updated property document
            return await get_property_by_id(db, property_id)
        return None # Property not found or not modified
    except PyMongoError as e:
        print(f"Error adding device to property {property_id}: {e}", file=sys.stderr)
        return None

# --- HistoricalUsageLog Collection Drivers (FR2.5, NFR-P1) ---

async def add_usage_log(db: AsyncIOMotorDatabase, log_data: HistoricalUsageLog) -> Optional[HistoricalUsageLog]:
    """
    Inserts a single time-series usage log.
    This collection MUST be a Time Series Collection in MongoDB for NFR-P1.
    """
    try:
        await db["usage_logs"].insert_one(log_data.model_dump())
        return log_data
    except PyMongoError as e:
        print(f"Error adding usage log: {e}", file=sys.stderr)
        return None

async def get_usage_logs(
    db: AsyncIOMotorDatabase, 
    mpan_id: str, # Note: This should match the mpan_id in your usage.py model
    start_date: datetime, 
    end_date: datetime
) -> List[HistoricalUsageLog]:
    """
    Retrieves all usage logs for a specific meter (mpan_id) 
    within a given time range.
    This query is optimized for Time Series Collections (NFR-P1).
    """
    logs = []
    try:
        # Time-series query: filter by mpan_id and timestamp range
        cursor = db["usage_logs"].find({
            "mpan_id": mpan_id,
            "timestamp": {
                "$gte": start_date,
                "$lt": end_date
            }
        })
        # Iterate over the async cursor
        async for log_doc in cursor:
            logs.append(HistoricalUsageLog(**log_doc))
        return logs
    except PyMongoError as e:
        print(f"Error retrieving usage logs for {mpan_id}: {e}", file=sys.stderr)
        return [] # Return empty list on error

