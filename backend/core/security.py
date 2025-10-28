
# backend/core/security.py

# This file implements core security logic for hashing and JWTs.
# Adheres to NFR-S1 (Authentication Security).
#
# NEW: We are now using 'bcrypt' directly to bypass 'passlib' environment errors.

import os
import bcrypt  # Import bcrypt directly
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv

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
    # Encode the password to bytes, required by bcrypt
    password_bytes = password.encode('utf-8')
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decode the hash back to a string to store in JSON-based MongoDB
    return hashed_password_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored hash."""
    try:
        # Encode both to bytes for comparison
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        # Check the password
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception as e:
        # Catch errors if the hash is invalid
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
        # Fallback to the default 30 minutes if no delta is provided
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

