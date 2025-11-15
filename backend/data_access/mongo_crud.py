# This file implements the base drivers for MongoDB access for all
# domain models *except* User (which is handled in database.py).
# This adheres to the "Modularity (Data Access Layer)" coding standard.
# All functions are async and include explicit error handling (NFR-S3).
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added `bulk_insert_usage_logs` function to persist
#   the simulated data from the file reader on startup.
# ---
import sys
from datetime import datetime
from typing import List, Optional, Union, Dict, Set, Tuple
import typing
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError, BulkWriteError
from fastapi import HTTPException
from starlette import status

# -------------------------------------------------
# FIXED IMPORTS (NO MORE backend.)
# -------------------------------------------------
from models.tariff import Tariff
from models.property import Property, Device, Homeowner, PropertyManager
from models.usage import HistoricalUsageLog
from models.user import UserRole
# -------------------------------------------------

# Full user type
FullUserType = Union[Homeowner, PropertyManager]


# --------------------------------------------------------------------
# Fetch User Context (Task: Fetch User Context - Sprint 2)
# --------------------------------------------------------------------
async def get_user_context_data(
    db: AsyncIOMotorDatabase, user: FullUserType
) -> Tuple[List[Property], Dict[int, Tariff]]:
    properties: List[Property] = []
    tariff_ids: Set[int] = set()
    tariffs: Dict[int, Tariff] = {}

    try:
        # Step 1 → Fetch Properties by Role
        if user.role == UserRole.HOMEOWNER:
            user = typing.cast(Homeowner, user)
            prop_doc = await db["properties"].find_one({"property_id": user.property_id})

            if prop_doc:
                prop = Property(**prop_doc)
                prop.devices = prop.devices or []
                properties.append(prop)
            else:
                print(
                    f"Warning: Homeowner {user.email} links to missing property {user.property_id}",
                    file=sys.stderr
                )

        elif user.role == UserRole.PROPERTY_MANAGER:
            user = typing.cast(PropertyManager, user)
            cursor = db["properties"].find({"portfolio_id": user.portfolio_id})

            async for prop_doc in cursor:
                prop = Property(**prop_doc)
                prop.devices = prop.devices or []
                properties.append(prop)

        if not properties:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No properties found for this user. Please complete profile setup."
            )

        # Step 2 → Collect tariff IDs
        for prop in properties:
            tariff_ids.add(prop.tariff_id)

        # Step 3 → Fetch tariffs
        for t_id in tariff_ids:
            tariff_doc = await get_tariff_by_id(db, t_id)
            if tariff_doc:
                tariffs[t_id] = tariff_doc
            else:
                print(
                    f"Warning: Missing tariff {t_id} referenced by property.",
                    file=sys.stderr
                )

        return properties, tariffs

    except HTTPException:
        raise
    except PyMongoError as e:
        print(f"Error (context): {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Database error.")
    except Exception as e:
        print(f"Unexpected error in get_user_context_data: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


# --------------------------------------------------------------------
# Tariff Functions
# --------------------------------------------------------------------
async def add_tariff(db: AsyncIOMotorDatabase, tariff_data: Tariff) -> Optional[Tariff]:
    try:
        await db["tariffs"].insert_one(tariff_data.model_dump())
        return tariff_data
    except PyMongoError as e:
        print(f"Error adding tariff: {e}", file=sys.stderr)
        return None


async def get_tariff_by_id(db: AsyncIOMotorDatabase, tariff_id: int) -> Optional[Tariff]:
    try:
        tariff_doc = await db["tariffs"].find_one({"tariff_id": tariff_id})
        if tariff_doc:
            return Tariff(**tariff_doc)
        return None
    except PyMongoError as e:
        print(f"Error retrieving tariff {tariff_id}: {e}", file=sys.stderr)
        return None


# --------------------------------------------------------------------
# Property & Device Functions
# --------------------------------------------------------------------
async def create_property(db: AsyncIOMotorDatabase, property_data: Property) -> Optional[Property]:
    try:
        await db["properties"].insert_one(property_data.model_dump())
        return property_data
    except PyMongoError as e:
        print(f"Error creating property: {e}", file=sys.stderr)
        return None


async def get_property_by_id(db: AsyncIOMotorDatabase, property_id: int) -> Optional[Property]:
    try:
        property_doc = await db["properties"].find_one({"property_id": property_id})
        if property_doc:
            return Property(**property_doc)
        return None
    except PyMongoError as e:
        print(f"Error retrieving property {property_id}: {e}", file=sys.stderr)
        return None


async def add_device_to_property(db: AsyncIOMotorDatabase, property_id: int, device_data: Device) -> Optional[Property]:
    try:
        result = await db["properties"].update_one(
            {"property_id": property_id},
            {"$push": {"devices": device_data.model_dump()}}
        )

        if result.modified_count == 1:
            return await get_property_by_id(db, property_id)

        return None
    except PyMongoError as e:
        print(f"Error adding device to property {property_id}: {e}", file=sys.stderr)
        return None


# --------------------------------------------------------------------
# Usage Log Functions (Sprint 2 + 3)
# --------------------------------------------------------------------
async def add_usage_log(db: AsyncIOMotorDatabase, log_data: HistoricalUsageLog) -> Optional[HistoricalUsageLog]:
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

    logs = []
    try:
        cursor = db["usage_logs"].find({
            "mpan_id": mpan_id,
            "timestamp": {"$gte": start_date, "$lt": end_date}
        })

        async for doc in cursor:
            logs.append(HistoricalUsageLog(**doc))

        return logs
    except PyMongoError as e:
        print(f"Error retrieving usage logs for {mpan_id}: {e}", file=sys.stderr)
        return []


# --------------------------------------------------------------------
# Bulk Insert (Task 2.2)
# --------------------------------------------------------------------
async def bulk_insert_usage_logs(
    db: AsyncIOMotorDatabase,
    logs: List[HistoricalUsageLog]
) -> int:

    if not logs:
        print("No logs provided for bulk insert.", file=sys.stdout)
        return 0

    print(f"Bulk inserting {len(logs)} logs...", file=sys.stdout)

    try:
        log_dicts = [log.model_dump() for log in logs]

        result = await db["usage_logs"].insert_many(log_dicts, ordered=False)

        count = len(result.inserted_ids)
        print(f"Inserted {count} logs successfully.", file=sys.stdout)
        return count

    except BulkWriteError as e:
        return e.details.get("nInserted", 0)

    except PyMongoError as e:
        print(f"Database error during bulk insert: {e}", file=sys.stderr)
        return 0

    except Exception as e:
        print(f"Unexpected error during bulk insert: {e}", file=sys.stderr)
        return 0
