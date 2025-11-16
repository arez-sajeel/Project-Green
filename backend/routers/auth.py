
# backend/routers/auth.py

# This file implements the API endpoints (routes) for authentication.
# ---
# MODIFIED FOR SPRINT 2 (Absolute Imports):
# - All imports are now absolute from the 'backend' root
#   (e.g., `from backend.models.user import ...`) to fix
#   ModuleNotFoundError.
# - `register_user` is updated to create full Homeowner/PropertyManager
#   documents, not just UserInDB.
# ---

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import sys
import typing # Added for type casting

#
# FIX 1: Use absolute imports
#
from backend.models.user import UserCreate, UserInDB, Token, UserRole
from backend.models.property import Homeowner, PropertyManager # Import full models
from typing import Optional
from backend.data_access.database import get_db, get_user_by_email, create_user
from backend.core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    get_current_active_user # Import the new dependency
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Create the router for authentication
router = APIRouter()

# --- Registration Endpoint ---

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED) # FIX: Was HTTP_21_CREATED
async def register_user(
    # Note: UserCreate does not have property_id/portfolio_id
    # This is a simplification for now. A real app would add them.
    user_in: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Handles new user registration.
    Follows the 'New User Sign-Up Route' flowchart.
    
    MODIFIED (Sprint 2):
    This now correctly creates a full Homeowner or PropertyManager
    document in the 'users' collection.
    """
    try:
        # 1. Check if user already exists
        existing_user = await get_user_by_email(db, user_in.email)
        
        # 2. If Yes: Return 409 Conflict
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )
        
        # 3. If No: Hash the password
        hashed_password = hash_password(user_in.password)
        
        # Create the user model for the database
        user_db_data = user_in.model_dump()
        user_db_data["hashed_password"] = hashed_password
        del user_db_data["password"] # Remove plain text password

        #
        # FIX 2: Create the *full* user model, not just UserInDB
        # This is required for our new `get_user_by_email` to work
        # Allow null role for users who haven't completed role selection
        #
        if user_in.role == UserRole.HOMEOWNER:
            # We add a placeholder property_id for new signups
            user_db_data.setdefault("property_id", 999) # Placeholder
            user_db = Homeowner(**user_db_data)
        elif user_in.role == UserRole.PROPERTY_MANAGER:
            # We add a placeholder portfolio_id for new signups
            user_db_data.setdefault("portfolio_id", 888) # Placeholder
            user_db = PropertyManager(**user_db_data)
        elif user_in.role is None or user_in.role == "":
            # User hasn't selected a role yet - create basic UserInDB
            user_db = UserInDB(**user_db_data)
        else:
             raise HTTPException(status_code=400, detail="Invalid user role")

        # 4. Create User Record in MongoDB - insert as dict to avoid validation issues
        users_collection = db["users"]
        user_dict = user_db.model_dump() if hasattr(user_db, 'model_dump') else user_db.dict()
        result = await users_collection.insert_one(user_dict)
        success = result.inserted_id is not None
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in database."
            )

        # 5. Generate JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_in.email}, expires_delta=access_token_expires
        )
        
        # 6. Return 201 Created & JWT
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in /register endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}"
        )

# --- Login Endpoint ---

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Handles user login.
    Follows the 'Client: POST /auth/login' flowchart.
    Uses OAuth2PasswordRequestForm, so username IS the email.
    """
    # 1. Query DB for user
    #    This now returns a full Homeowner/PropertyManager model
    user = await get_user_by_email(db, form_data.username)

    # 2. Verify Password Match
    if not user or not verify_password(form_data.password, user.hashed_password):
        # 3. If No: Return 401 Error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 4. If Yes: Generate JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # 5. Return 200 OK & JWT
    return {"access_token": access_token, "token_type": "bearer"}


# --- Get Current User Endpoint ---

@router.get("/me")
async def get_current_user_info(
    current_user: typing.Union[Homeowner, PropertyManager, UserInDB] = Depends(get_current_active_user)
):
    """
    Returns the current authenticated user's information.
    Used to check if user has completed role selection.
    """
    return {
        "email": current_user.email,
        "role": current_user.role if hasattr(current_user, 'role') else None,
        "property_id": getattr(current_user, "property_id", None),
        "portfolio_id": getattr(current_user, "portfolio_id", None)
    }


# --- Update User Role Endpoint ---

@router.put("/update-role")
async def update_user_role(
    role_data: dict,
    current_user: typing.Union[Homeowner, PropertyManager, UserInDB] = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Updates the user's role after they complete role selection.
    This is used when a user registers but doesn't complete role selection.
    """
    try:
        new_role = role_data.get("role")
        
        if not new_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role is required"
            )
        
        # Validate role
        if new_role not in [UserRole.HOMEOWNER, UserRole.PROPERTY_MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'Homeowner' or 'PropertyManager'"
            )
        
        # Update user role in database and add required fields
        users_collection = db["users"]
        update_fields = {"role": new_role}
        
        # Add required fields based on role
        if new_role == UserRole.HOMEOWNER:
            update_fields["property_id"] = 999  # Placeholder property_id
        elif new_role == UserRole.PROPERTY_MANAGER:
            update_fields["portfolio_id"] = 888  # Placeholder portfolio_id
        
        result = await users_collection.update_one(
            {"email": current_user.email},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user role"
            )
        
        return {
            "message": "Role updated successfully",
            "email": current_user.email,
            "role": new_role
        }
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in /update-role endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}"
        )

