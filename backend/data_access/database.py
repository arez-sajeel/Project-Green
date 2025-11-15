# backend/data_access/database.py

# This file implements the Data Access Layer, as per our Coding Standards.
# All database operations are isolated here.
# NOTE: This file is now using 'motor', the ASYNCHRONOUS MongoDB driver.
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added Redis connection management for NFR-P2 (Data Latency).
# ---

import os
import sys
from typing import Union, Optional, AsyncGenerator

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Redis (Sprint 2)
import redis.asyncio as aioredis
from redis.asyncio import Redis

# -------------------------------------------------
# FIXED IMPORTS (no more backend.)
# -------------------------------------------------
from models.user import UserInDB
from models.property import Homeowner, PropertyManager
# -------------------------------------------------

# Load environment variables
load_dotenv()

# ----------------------
# MongoDB Configuration
# ----------------------
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL not set in .env file")

# ----------------------
# Redis Configuration
# ----------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# ----------------------
# MongoDB Client
# ----------------------
try:
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
except Exception as e:
    print(f"Failed to create Motor client: {e}", file=sys.stderr)
    mongo_client = None

# ----------------------
# Redis Client
# ----------------------
try:
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Failed to create Redis client: {e}", file=sys.stderr)
    redis_client = None


# -------------------------------
# Dependency: Get Mongo Database
# -------------------------------
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    if mongo_client is None:
        raise Exception("MongoDB client is not initialized.")

    yield mongo_client.get_database("geo_db")


# ------------------------------
# Mongo Connection Handlers
# ------------------------------
async def connect_to_mongo():
    if mongo_client:
        try:
            await mongo_client.admin.command("ping")
            print("MongoDB connection successful.", file=sys.stdout)
        except Exception as e:
            print(f"MongoDB connection failed: {e}", file=sys.stderr)
    else:
        print("MongoDB client not created.", file=sys.stderr)


async def close_mongo_connection():
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.", file=sys.stdout)


# ------------------------------
# Redis Dependency + Handlers
# ------------------------------
async def get_redis_client() -> AsyncGenerator[Redis, None]:
    if redis_client is None:
        raise Exception("Redis client is not initialized.")
    yield redis_client


async def connect_to_redis():
    if redis_client:
        try:
            await redis_client.ping()
            print("Redis connection successful.", file=sys.stdout)
        except Exception as e:
            print(f"Redis connection failed: {e}", file=sys.stderr)
    else:
        print("Redis client not created.", file=sys.stderr)


async def close_redis_connection():
    if redis_client:
        await redis_client.aclose()
        print("Redis connection closed.", file=sys.stdout)


# ------------------------------
# Database User Functions
# ------------------------------

FullUserType = Union[Homeowner, PropertyManager]

async def get_user_by_email(
    db: AsyncIOMotorDatabase, email: str
) -> Optional[Union[FullUserType, UserInDB]]:
    """
    Returns the correct user model based on their role.
    """

    try:
        user_data = await db["users"].find_one({"email": email})

        if user_data:
            role = user_data.get("role")

            if role == "Homeowner":
                return Homeowner(**user_data)

            if role == "PropertyManager":
                return PropertyManager(**user_data)

            if role is None or role == "":
                return UserInDB(**user_data)

        return None

    except Exception as e:
        print(f"Error in get_user_by_email: {e}", file=sys.stderr)
        return None


async def create_user(db: AsyncIOMotorDatabase, user: UserInDB) -> bool:
    """
    Creates a new user document in the DB.
    """
    try:
        await db["users"].insert_one(user.model_dump())
        return True

    except Exception as e:
        print(f"Error creating user: {e}", file=sys.stderr)
        return False
