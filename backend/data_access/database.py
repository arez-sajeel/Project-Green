
# backend/data_access/database.py

# This file implements the Data Access Layer, as per our Coding Standards.
# All database operations are isolated here.
# NOTE: This file is now using 'motor', the ASYNCHRONOUS MongoDB driver.

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from models.user import UserInDB, UserBase  # Use absolute import
import sys # To handle print statements for logging

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

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> UserInDB | None:
    """
    Finds a user by their email address.
    This is now an async operation.
    """
    # 'find_one' is now an awaitable coroutine from 'motor'
    user_data = await db["users"].find_one({"email": email})
    
    if user_data:
        return UserInDB(**user_data)
    return None

async def create_user(db: AsyncIOMotorDatabase, user: UserInDB) -> bool:
    """
    Creates a new user record in the 'users' collection.
    This is now an async operation.
    """
    try:
        # 'insert_one' is now an awaitable coroutine from 'motor'
        await db["users"].insert_one(user.model_dump())
        return True
    except Exception as e:
        print(f"Error creating user: {e}", file=sys.stderr)
        return False

