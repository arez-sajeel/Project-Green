# This file implements the base drivers for MongoDB access for all
# domain models *except* User (which is handled in database.py).
# This adheres to the "Modularity (Data Access Layer)" coding standard.
# All functions are async and include explicit error handling (NFR-S3).

import sys
from datetime import datetime
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
from models.tariff import Tariff
from models.property import Property, Device
from models.usage import HistoricalUsageLog

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
    mpan_id: str, 
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

