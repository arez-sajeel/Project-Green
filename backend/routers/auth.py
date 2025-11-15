
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
import typing
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

# -------------------------------------------------
# FIXED IMPORTS (no more: from backend....)
# -------------------------------------------------
from models.user import UserCreate, UserInDB, Token, UserRole
from models.property import Homeowner, PropertyManager
from data_access.database import get_db, get_user_by_email, create_user
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_active_user
)

# Load environment variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

router = APIRouter()

# --- Registration Endpoint ---

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        existing_user = await get_user_by_email(db, user_in.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        hashed_password = hash_password(user_in.password)

        user_db_data = user_in.model_dump()
        user_db_data["hashed_password"] = hashed_password
        del user_db_data["password"]

        # Create full role models
        if user_in.role == UserRole.HOMEOWNER:
            user_db_data.setdefault("property_id", 999)
            user_db = Homeowner(**user_db_data)
        elif user_in.role == UserRole.PROPERTY_MANAGER:
            user_db_data.setdefault("portfolio_id", 888)
            user_db = PropertyManager(**user_db_data)
        elif user_in.role is None or user_in.role == "":
            user_db = UserInDB(**user_db_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid user role")

        users_collection = db["users"]
        user_dict = user_db.model_dump() if hasattr(user_db, "model_dump") else user_db.dict()

        result = await users_collection.insert_one(user_dict)

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user in database."
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_in.email}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /register: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )


# --- Login Endpoint ---

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user = await get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# --- Get Current User ---

@router.get("/me")
async def get_current_user_info(
    current_user: typing.Union[Homeowner, PropertyManager, UserInDB] = Depends(get_current_active_user)
):
    return {
        "email": current_user.email,
        "role": current_user.role if hasattr(current_user, "role") else None,
        "property_id": getattr(current_user, "property_id", None),
        "portfolio_id": getattr(current_user, "portfolio_id", None),
    }


# --- Update User Role ---

@router.put("/update-role")
async def update_user_role(
    role_data: dict,
    current_user: typing.Union[Homeowner, PropertyManager, UserInDB] = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        new_role = role_data.get("role")

        if not new_role:
            raise HTTPException(status_code=400, detail="Role is required")

        if new_role not in [UserRole.HOMEOWNER, UserRole.PROPERTY_MANAGER]:
            raise HTTPException(status_code=400, detail="Invalid role")

        users_collection = db["users"]

        update_fields = {"role": new_role}

        if new_role == UserRole.HOMEOWNER:
            update_fields["property_id"] = 999
        elif new_role == UserRole.PROPERTY_MANAGER:
            update_fields["portfolio_id"] = 888

        result = await users_collection.update_one(
            {"email": current_user.email},
            {"$set": update_fields}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update user role")

        return {"message": "Role updated", "role": new_role}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /update-role: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
