# backend/data_access/database.py

# This file implements the Data Access Layer, as per our Coding Standards.
# All database operations are isolated here.
# NOTE: This file is now using 'motor', the ASYNCHRONOUS MongoDB driver.
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added Redis connection management for NFR-P2 (Data Latency).
# ---

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from typing import Union, Optional, AsyncGenerator # NEW: Added AsyncGenerator
import sys # To handle print statements for logging

# NEW (Sprint 2): Import async Redis
import redis.asyncio as aioredis
from redis.asyncio import Redis 

# Use absolute imports
from backend.models.user import UserInDB
from backend.models.property import Homeowner, PropertyManager

# Load environment variables from .env file
load_dotenv()

# --- MongoDB Configuration ---
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise ValueError("MONGODB_URL not set in .env file")

# --- NEW (Sprint 2): Redis Configuration ---
# Default to localhost if not set in .env
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# --- MongoDB Client Initialization ---
try:
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
except Exception as e:
    print(f"Failed to create Motor client: {e}", file=sys.stderr)
    mongo_client = None

# --- NEW (Sprint 2): Redis Client Initialization ---
# This client is shared across the app, just like the mongo_client
try:
    # We use 'decode_responses=True' so Python gets strings, not bytes.
    # This simplifies our code significantly.
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Failed to create Redis client: {e}", file=sys.stderr)
    redis_client = None


# --- MongoDB Connection Functions ---

async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]: # FIX: Use AsyncGenerator
    """
    Dependency injector to get the database instance.
    This is called for every request that needs a db connection.
    It yields the 'geo_db' database from our single, shared client.
    """
    if mongo_client is None:
        raise Exception("Database client is not initialized.")
    # Use 'yield' to ensure the dependency is recognized by FastAPI
    yield mongo_client.get_database("geo_db")

async def connect_to_mongo():
    """
    Connects to MongoDB and pings the server.
    This is called once on application startup.
    """
    if mongo_client:
        try:
            # Ping the server to confirm a successful connection
            await mongo_client.admin.command('ping')
            print("MongoDB connection successful.", file=sys.stdout)
        except Exception as e:
            print(f"MongoDB connection failed: {e}", file=sys.stderr)
    else:
        print("MongoDB client not created. Skipping connection.", file=sys.stderr)


async def close_mongo_connection():
    """Closes the MongoDB connection."""
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.", file=sys.stdout)

# --- NEW (Sprint 2): Redis Connection Functions ---

async def get_redis_client() -> AsyncGenerator[Redis, None]:
    """
    Dependency injector to get the Redis client instance.
    This is called for every request that needs a Redis connection.
    """
    if redis_client is None:
        raise Exception("Redis client is not initialized.")
    yield redis_client

async def connect_to_redis():
    """
    Connects to Redis and pings the server.
    This is called once on application startup.
    """
    if redis_client:
        try:
            # Ping the server to confirm a successful connection
            await redis_client.ping()
            print("Redis connection successful.", file=sys.stdout)
        except Exception as e:
            print(f"Redis connection failed: {e}", file=sys.stderr)
    else:
        print("Redis client not created. Skipping connection.", file=sys.stderr)

async def close_redis_connection():
    """Closes the Redis connection."""
    if redis_client:
        await redis_client.aclose() # Use aclose() for async client
        print("Redis connection closed.", file=sys.stdout)

# --- Database Operation Functions ---

# Define a type hint for the full user models
FullUserType = Union[Homeowner, PropertyManager]

async def get_user_by_email(
    db: AsyncIOMotorDatabase, email: str
) -> Optional[Union[FullUserType, UserInDB]]:
    """
    Finds a user by their email address.
    
    MODIFIED (Sprint 2):
    This function now returns the full Homeowner or PropertyManager
    model, which includes critical fields like `property_id` or
    `portfolio_id` required for NFR-S2 access control.
    
    Can also return UserInDB for users who haven't completed role selection.
    """
    try:
        user_data = await db["users"].find_one({"email": email})
        
        if user_data:
            # Pydantic will automatically parse the correct model
            # based on the 'role' field and its corresponding properties
            # (e.g., property_id for Homeowner).
            role = user_data.get("role")
            
            if role == "Homeowner":
                return Homeowner(**user_data)
            elif role == "PropertyManager":
                return PropertyManager(**user_data)
            elif role is None or role == "":
                # User hasn't completed role selection yet
                return UserInDB(**user_data)
        
        return None
    except Exception as e:
        print(f"Error in get_user_by_email: {e}", file=sys.stderr)
        return None


async def create_user(db: AsyncIOMotorDatabase, user: UserInDB) -> bool:
    """
    Creates a new user record in the 'users' collection.
    This is now an async operation.
    
    NOTE: This function still correctly takes a UserInDB, as the
    'register_user' endpoint in auth.py is responsible for creating
    the full Homeowner/PropertyManager document (which we need to implement).
    
    For now, we assume the 'users' collection stores the full document.
    """
    try:
        # 'insert_one' is now an awaitable coroutine from 'motor'
        await db["users"].insert_one(user.model_dump())
        return True
    except Exception as e:
        print(f"Error creating user: {e}", file=sys.stderr)
        return False
