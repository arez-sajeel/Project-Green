
# This is the main entry point for our FastAPI application.
# It initializes the FastAPI app and includes all the necessary routers.
# ---
# MODIFIED FOR SPRINT 2 (Fetch User Context):
# - Imported and included the new `context_router`
# ---

from fastapi import FastAPI
from backend.routers import auth  # Use absolute import
from backend.routers import context # NEW (Sprint 2)
from backend.data_access.database import connect_to_mongo, close_mongo_connection
import sys
import typing

# Initialize the main FastAPI application instance
app = FastAPI(
    title="Green Energy Optimizer API",
    description="API for managing energy data and providing optimization reports.",
    version="0.2.0" # Incremented version for Sprint 2
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


# --- Include Routers ---

# Include the authentication router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# NEW (Sprint 2): Include the user context router
app.include_router(context.router, prefix="/users", tags=["User Context"])
# Note: The endpoint will be GET /users/context


# Root endpoint for basic health check
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root GET endpoint.
    Provides a simple welcome message and confirms the API is running.
    """
    return {"message": "Welcome to the Green Energy Optimizer API (v0.2.0)"}
