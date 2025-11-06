# This is the main entry point for our FastAPI application.
# It initializes the FastAPI app and includes all the necessary routers.
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added Redis connection handlers for startup/shutdown.
# - Added data loading and NFR-P2 simulation logic on startup.
# - Removed persistence "STUB" and now calls mongo_crud.
# - Added CORS middleware for frontend integration.
# ---

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth  # Use absolute import
from backend.routers import context 
import sys
import typing
import os # NEW (S2): To get file paths from .env
import asyncio # NEW (S2): For the simulation background task
from contextlib import asynccontextmanager # NEW (S2): Preferred for startup/shutdown

# --- NEW (S2): Import all our S1/S2 modules ---
from backend.data_access.database import (
    connect_to_mongo, 
    close_mongo_connection,
    connect_to_redis,    # New
    close_redis_connection, # New
    redis_client,        # New: Import the client instance
    get_db               # New: To get a DB session for persistence
)
from backend.data_access.file_readers import load_and_simulate_ukpn_data
# NEW (Task 2.2): Import the bulk insert function
from backend.data_access.mongo_crud import bulk_insert_usage_logs 
from backend.models.usage import HistoricalUsageLog
from typing import List
from itertools import cycle # NEW (S2): To loop our simulation
# We must import this to get a DB session outside a request
from asyncstdlib import anext 


# --- NEW (S2): NFR-P2 Real-time Simulation Task ---

async def simulate_real_time_feed(logs: List[HistoricalUsageLog]):
    """
    A background task that simulates a live data feed (NFR-P2).
    It loops through the historical data and pushes one new
    reading to the Redis cache every 5 seconds.
    
    The React frontend (FR3.1) will read from this key.
    """
    print("NFR-P2 Simulation: Starting real-time feed simulation...", file=sys.stdout)
    
    # Use 'cycle' to loop through the logs forever
    simulated_stream = cycle(logs)
    
    if redis_client is None:
        print("NFR-P2 Simulation: Redis client not available. Task stopping.", file=sys.stderr)
        return

    try:
        for log_entry in simulated_stream:
            # We push the data to a single, well-known key
            # The frontend will *only* read from 'real_time_usage'
            # We use .set() which just overwrites the key
            
            # Simple JSON-like string for the frontend
            # In a real app, we might use JSON, but this is simple (P2)
            # NOTE: We must convert timestamp to a string
            payload = f"{log_entry.timestamp.isoformat()}|{log_entry.kwh_consumption:.2f}"
            
            await redis_client.set("real_time_usage", payload)
            
            # Wait for 5 seconds, as per NFR-P2
            await asyncio.sleep(5)
            
    except asyncio.CancelledError:
        print("NFR-P2 Simulation: Task cancelled.", file=sys.stdout)
    except Exception as e:
        print(f"NFR-P2 Simulation: Task failed: {e}", file=sys.stderr)


# --- NEW (S2): Replaced startup/shutdown events with lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown logic.
    This is the modern replacement for @app.on_event.
    """
    print("FastAPI application starting up...", file=sys.stdout)
    
    # 1. Connect to Databases
    await connect_to_mongo()
    await connect_to_redis() # New
    
    # --- 2. Task 2.2: Load Usage Data ---
    # Get the data file path from our .env file
    # We'll assume it's set as UKPN_DATA_FILE
    data_file = os.getenv("UKPN_DATA_FILE", "data/ukpn_mock_data.csv")
    
    try:
        # This one function performs all of Task 2.2's file logic
        logs = load_and_simulate_ukpn_data(data_file)
        
        # --- Task 2.2: Persist Data to MongoDB ---
        # This is the final step, removing the STUB
        if logs:
            try:
                # We get a DB session to use outside a request
                db_session_gen = get_db()
                db = await anext(db_session_gen)
                
                # Call our new function from mongo_crud.py
                await bulk_insert_usage_logs(db, logs) 
                
            except Exception as e:
                print(f"Error (Task 2.2): Failed during bulk persistence: {e}", file=sys.stderr)
        
        
            # --- 3. Start NFR-P2 Simulation ---
            # We only start the simulation if we have logs
            asyncio.create_task(simulate_real_time_feed(logs))
        
    except Exception as e:
        print(f"FATAL: Failed to load or simulate data on startup: {e}", file=sys.stderr)
        # We could exit here if data is critical
    
    
    # --- Logic runs until shutdown ---
    yield
    # --- App is shutting down ---
    
    print("FastAPI application shutting down...", file=sys.stdout)
    await close_mongo_connection()
    await close_redis_connection() # New


# Initialize the main FastAPI application instance
app = FastAPI(
    title="Green Energy Optimizer API",
    description="API for managing energy data and providing optimization reports.",
    version="0.2.2", # Incremented version for Task 2.2
    lifespan=lifespan  # NEW (S2): Use the lifespan context manager
)

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include Routers ---

# Include the authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include the user context router
app.include_router(context.router, prefix="/users", tags=["User Context"])
# Note: The endpoint will be GET /users/context


# Root endpoint for basic health check
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root GET endpoint.
    Provides a simple welcome message and confirms the API is running.
    """
    return {"message": "Welcome to the Green Energy Optimizer API (v0.2.2)"}

