
# backend/models/user.py

# This file defines the Pydantic models (data schemas) for user authentication.
# These models are used by FastAPI for request validation and response formatting.
# Adheres to Naming Standards (PascalCase for classes) and Mandatory Type Hinting.

from pydantic import BaseModel, EmailStr
from enum import Enum

# Defines the roles available in the system.
# This is crucial for NFR-S2 (Role-Based Access Control).
class UserRole(str, Enum):
    """Enumeration of valid user roles."""
    HOMEOWNER = "Homeowner"
    PROPERTY_MANAGER = "PropertyManager"

class UserBase(BaseModel):
    """
    Base user model with shared fields.
    Contains common information that is validated for both input and output.
    """
    email: EmailStr  # Ensures the email provided is a valid email format
    role: UserRole   # Enforces that the role must be one of the UserRole enum values

class UserCreate(UserBase):
    """
    Model used for creating a new user (Sign-Up).
    Inherits email and role from UserBase and adds the password field.
    This model is used as the request body for the /register endpoint.
    """
    password: str    # Plain-text password provided by the user

class UserInDB(UserBase):
    """
    Model representing a user as stored in the MongoDB database.
    Inherits email and role, but stores the hashed password, not the plain text.
    This adheres to NFR-S1 (Authentication Security).
    """
    hashed_password: str

class Token(BaseModel):
    """
    Response model for successful authentication (Login or Register).
    This is what the user receives, as per the flowcharts.
    """
    access_token: str
    token_type: str = "bearer"  # Defaults to "bearer", a standard for JWTs
