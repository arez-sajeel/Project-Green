
# This file centralizes all data access functions to adhere to the
# D.R.Y. (P1) and Modularity (2.2) coding standards.
# Other modules can now import directly from 'data_access'.

# --- From database.py ---
# Core connection logic and User auth functions (Task 3.a)
from .database import (
    get_db,
    connect_to_mongo,
    close_mongo_connection,
    get_user_by_email,
    create_user
)

# --- From mongo_crud.py ---
# Domain model CRUD functions (Task 1.b)
from .mongo_crud import (
    add_tariff,
    get_tariff_by_id,
    create_property,
    get_property_by_id,
    add_device_to_property,
    add_usage_log,
    get_usage_logs
)

# --- From file_readers.py ---
# Local file reader drivers (Task 1.b)
from .file_readers import (
    load_mock_tariffs_from_csv,
    load_ukpn_data
)

