

# This is the main entry point for our FastAPI application.
# It initializes the FastAPI app and includes all the necessary routers.
# ---
# MODIFIED FOR TASK 1.b:
# - Added on_event handlers to connect and disconnect from MongoDB on startup/shutdown.
# ---

from fastapi import FastAPI
from routers import auth  # Use absolute import (no dot)
from data_access.database import connect_to_mongo, close_mongo_connection # Task 1.b
import sys

# Initialize the main FastAPI application instance
app = FastAPI(
    title="Green Energy Optimizer API",
    description="API for managing energy data and providing optimization reports.",
    version="0.1.0"
)

# --- Task 1.b: Database Connection Event Handlers ---

@app.on_event("startup")
async def startup_event():
    """
    On application startup, connect to the MongoDB database.
    """
    print("FastAPI application starting up...", file=sys.stdout)
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """
    On application shutdown, close the MongoDB connection.
    """
    print("FastAPI application shutting down...", file=sys.stdout)
    await close_mongo_connection()

# --- End Task 1.b ---


# Include the authentication router
# All endpoints from `auth.py` will be prefixed with /auth
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Root endpoint for basic health check
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root GET endpoint.
    Provides a simple welcome message and confirms the API is running.
    """
    return {"message": "Welcome to the Green Energy Optimizer API"}

