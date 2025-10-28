
# backend/main.py

# This is the main entry point for our FastAPI application.
# It initializes the FastAPI app and includes all the necessary routers.

from fastapi import FastAPI
from routers import auth  # Use absolute import (no dot)

# Initialize the main FastAPI application instance
app = FastAPI(
    title="Green Energy Optimizer API",
    description="API for managing energy data and providing optimization reports.",
    version="0.1.0"
)

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

