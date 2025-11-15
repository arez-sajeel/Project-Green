# This is the main entry point for our FastAPI application.
# It initializes the FastAPI app and includes all the necessary routers.
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added Redis connection handlers for startup/shutdown.
# - Added data loading and NFR-P2 simulation logic on startup.
# - Removed persistence "STUB" and now calls mongo_crud.
# - Added CORS middleware for frontend integration.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth
from routers import context
from routers import property_manager  

import sys
import typing
import os
import asyncio
from contextlib import asynccontextmanager

# --- NEW (S2): Import all our S1/S2 modules ---
from data_access.database import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_redis,
    close_redis_connection,
    redis_client,
    get_db
)
from data_access.file_readers import load_and_simulate_ukpn_data
from data_access.mongo_crud import bulk_insert_usage_logs
from models.usage import HistoricalUsageLog

from typing import List
from itertools import cycle
from asyncstdlib import anext


# --- NEW (S2): NFR-P2 Real-time Simulation Task ---
async def simulate_real_time_feed(logs: List[HistoricalUsageLog]):
    print("NFR-P2 Simulation: Starting real-time feed simulation...", file=sys.stdout)

    simulated_stream = cycle(logs)

    if redis_client is None:
        print("NFR-P2 Simulation: Redis client not available. Task stopping.", file=sys.stderr)
        return

    try:
        for log_entry in simulated_stream:
            payload = f"{log_entry.timestamp.isoformat()}|{log_entry.kwh_consumption:.2f}"
            await redis_client.set("real_time_usage", payload)
            await asyncio.sleep(5)

    except asyncio.CancelledError:
        print("NFR-P2 Simulation: Task cancelled.", file=sys.stdout)
    except Exception as e:
        print(f"NFR-P2 Simulation: Task failed: {e}", file=sys.stderr)


# --- NEW (S2): Replaced startup/shutdown events with lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI application starting up...", file=sys.stdout)

    # 1. Connect to Databases
    await connect_to_mongo()
    await connect_to_redis()

    # 2. Load Usage Data
    data_file = os.getenv("UKPN_DATA_FILE", "data/ukpn_mock_data.csv")

    try:
        logs = load_and_simulate_ukpn_data(data_file)

        if logs:
            try:
                db_session_gen = get_db()
                db = await anext(db_session_gen)

                await bulk_insert_usage_logs(db, logs)

            except Exception as e:
                print(f"Error (Task 2.2): Failed during bulk persistence: {e}", file=sys.stderr)

            asyncio.create_task(simulate_real_time_feed(logs))

    except Exception as e:
        print(f"FATAL: Failed to load or simulate data on startup: {e}", file=sys.stderr)

    yield

    print("FastAPI application shutting down...", file=sys.stdout)
    await close_mongo_connection()
    await close_redis_connection()


# Initialize FastAPI
app = FastAPI(
    title="Green Energy Optimizer API",
    description="API for managing energy data and providing optimization reports.",
    version="0.2.2",
    lifespan=lifespan
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(context.router, prefix="/users", tags=["User Context"])
app.include_router(property_manager.router, prefix="/properties", tags=["Property Manager"])  # ✅ ADDED

# --- Root ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Green Energy Optimizer API (v0.2.2)"}
