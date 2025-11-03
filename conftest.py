# It helps pytest discover our application modules.

import sys
import os

# Add the project root to the Python path
# This allows our tests in the 'tests/' directory to successfully
# import modules from the 'backend/' directory, e.g., 'from backend.models...'
