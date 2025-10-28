
# backend/routers/auth.py

# This file implements the API endpoints (routes) for authentication.
# It follows the flowcharts for /register and /login.
# It adheres to Modularity rules by calling helper functions from:
# - data_access.database (for DB operations)
# - core.security (for hashing and JWTs)

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.user import UserCreate, UserInDB, Token, UserRole
from data_access.database import get_db, get_user_by_email, create_user
from core.security import hash_password, verify_password, create_access_token
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv
from datetime import timedelta
import sys

# Load environment variables
load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Create the router for authentication
router = APIRouter()

# --- Registration Endpoint ---

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Handles new user registration.
    Follows the 'New User Sign-Up Route' flowchart.
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
        user_db = UserInDB(
            email=user_in.email,
            role=user_in.role,
            hashed_password=hashed_password
        )
        
        # 4. Create User Record in MongoDB
        success = await create_user(db, user_db)
        
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
        # Re-raise HTTP exceptions (like the 409) directly
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error in /register endpoint: {e}", file=sys.stderr)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred."
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
    user = await get_user_by_email(db, form_data.username)

    # 2. Verify Password Match
    #    FIX: Use dot notation (user.hashed_password) not dict (user['...'])
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

