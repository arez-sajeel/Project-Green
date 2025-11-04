# This file makes our Pydantic models accessible as a Python package.
# We import all the main classes from our model files so they can be
# imported directly from 'models' (e.g., from models import User, Property).
# This simplifies imports in routers and data_access layers.

# From backend/models/user.py
from .user import (
    UserBase,
    UserCreate,
    UserInDB,
    UserRole,
    Token
)

# From backend/models/property.py
from .property import (
    Device,
    Property,
    Homeowner,
    PropertyManager
)

# From backend/models/tariff.py
from .tariff import Tariff

# From backend/models/usage.py
from .usage import HistoricalUsageLog

# --- START OF MODIFICATION (SPRINT 2.4) ---
# From backend/models/scenario.py
from .scenario import ShiftValidationRequest
# --- END OF MODIFICATION (SPRINT 2.4) ---
