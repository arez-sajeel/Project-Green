
# backend/data_access/database.py

# This file implements the Data Access Layer, as per our Coding Standards.
# All database operations are isolated here.
# NOTE: This file is now using 'motor', the ASYNCHRONOUS MongoDB driver.
# ---
# MODIFIED FOR SPRINT 2 (Fetch User Context):
# - Modified get_user_by_email to return the full Pydantic model
#   (Homeowner or PropertyManager) instead of just UserInDB.
# - This is critical for the auth dependency to get property_id/portfolio_id.
# ---

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from typing import Union, Optional
import sys # To handle print statements for logging

# Use absolute imports
from backend.models.user import UserInDB
from backend.models.property import Homeowner, PropertyManager

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL not set in .env file")

# Create the async client at the module level
# This client object is managed by motor's connection pool
try:
    client = AsyncIOMotorClient(MONGODB_URL)
except Exception as e:
    print(f"Failed to create Motor client: {e}", file=sys.stderr)
    client = None

async def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency injector to get the database instance.
    This is called for every request that needs a db connection.
    It yields the 'geo_db' database from our single, shared client.
    """
    if client is None:
        raise Exception("Database client is not initialized.")
    # Use 'yield' to ensure the dependency is recognized by FastAPI
    yield client.get_database("geo_db")

async def connect_to_mongo():
    """
    Connects to MongoDB and pings the server.
    This is called once on application startup.
    """
    if client:
        try:
            # Ping the server to confirm a successful connection
            await client.admin.command('ping')
            print("MongoDB connection successful.", file=sys.stdout)
        except Exception as e:
            print(f"MongoDB connection failed: {e}", file=sys.stderr)
    else:
        print("MongoDB client not created. Skipping connection.", file=sys.stderr)


async def close_mongo_connection():
    """Closes the MongoDB connection."""
    if client:
        client.close()
        print("MongoDB connection closed.", file=sys.stdout)

# --- Database Operation Functions ---

# Define a type hint for the full user models
FullUserType = Union[Homeowner, PropertyManager]

async def get_user_by_email(
    db: AsyncIOMotorDatabase, email: str
) -> Optional[FullUserType]:
    """
    Finds a user by their email address.
    
    MODIFIED (Sprint 2):
    This function now returns the full Homeowner or PropertyManager
    model, which includes critical fields like `property_id` or
    `portfolio_id` required for NFR-S2 access control.
    """
    try:
        user_data = await db["users"].find_one({"email": email})
        
        if user_data:
            # Pydantic will automatically parse the correct model
            # based on the 'role' field and its corresponding properties
            # (e.g., property_id for Homeowner).
            if user_data.get("role") == "Homeowner":
                return Homeowner(**user_data)
            elif user_data.get("role") == "PropertyManager":
                return PropertyManager(**user_data)
        
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
