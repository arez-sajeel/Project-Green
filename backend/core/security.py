
# backend/core/security.py

# This file implements core security logic for hashing and JWTs.
# Adheres to NFR-S1 (Authentication Security).
# ---
# MODIFIED FOR SPRINT 2 (Fetch User Context):
# - Added `oauth2_scheme` definition.
# - Added `get_current_active_user` dependency. This is the new
#   standard for all protected endpoints, as it fetches the
#   *full* user model (Homeowner/PropertyManager) for NFR-S2.
# ---

import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from typing import Union, Optional

# Use absolute imports
from backend.data_access.database import get_db, get_user_by_email
from backend.models.property import Homeowner, PropertyManager
from backend.models.user import UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in .env file")

# --- Password Hashing Functions (using bcrypt directly) ---

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_password_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored hash."""
    try:
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception as e:
        print(f"Bcrypt verification error: {e}")
        return False

# --- JSON Web Token (JWT) Functions ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a new JSON Web Token (JWT).
    Accepts an 'expires_delta' to set expiry time.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- NEW (Sprint 2): Authentication Dependency ---

# This tells FastAPI where to look for the token ("tokenUrl" is relative)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define a type hint for the full user models
FullUserType = Union[Homeowner, PropertyManager, UserInDB]

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> FullUserType:
    """
    The primary authentication dependency for protected endpoints.
    
    1. Decodes the JWT from the "Authorization: Bearer <token>" header.
    2. Extracts the user's email ('sub').
    3. Fetches the *full* user model (Homeowner, PropertyManager, or UserInDB) from the DB.
    
    This satisfies NFR-S2 by providing the user's role and associated
    property_id/portfolio_id for data access control.
    UserInDB is returned for users who haven't completed role selection.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    except ValidationError:
        raise credentials_exception
        
    # 2. Fetch Full User Model from DB
    user = await get_user_by_email(db, email=email)
    
    if user is None:
        raise credentials_exception
        
    # 3. Return the full Homeowner or PropertyManager model
    return user
