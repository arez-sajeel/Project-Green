
# backend/data_access/file_readers.py

# This file implements the base drivers for reading local files (CSV/JSON),
# as specified in Task 1.b.
# This adheres to the "Modularity (Data Access Layer)" coding standard.
# It uses pandas for efficient file parsing.

import pandas as pd
from typing import List, Dict, Any, Optional # FIX: Added 'Optional'
import sys

def load_mock_tariffs_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads mock tariff data from a local CSV file.
    Converts the DataFrame to a list of dictionaries for ingestion.
    Adheres to P3/NFR-S3 by handling file errors.
    """
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path)
        
        # Convert to list of dictionaries
        # This format is required by the MongoDB insert_many() function
        tariffs = df.to_dict(orient='records')
        
        print(f"Successfully loaded {len(tariffs)} tariffs from {file_path}", file=sys.stdout)
        return tariffs
        
    except FileNotFoundError:
        print(f"Error: Mock tariff file not found at {file_path}", file=sys.stderr)
        return []
    except pd.errors.ParserError:
        print(f"Error: Failed to parse mock tariff CSV at {file_path}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred reading {file_path}: {e}", file=sys.stderr)
        return []

def load_ukpn_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Reads the UKPN LCL smart meter data from a local file.
    Returns a pandas DataFrame for processing in Sprint 2 (Load Usage Data).
    Adheres to P3/NFR-S3 by handling file errors.
    """
    try:
        # Read the data file (assuming CSV for this driver)
        df = pd.read_csv(file_path)
        
        print(f"Successfully loaded UKPN data from {file_path}", file=sys.stdout)
        return df
        
    except FileNotFoundError:
        print(f"Error: UKPN data file not found at {file_path}", file=sys.stderr)
        return None
    except pd.errors.ParserError:
        print(f"Error: Failed to parse UKPN data file at {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred reading {file_path}: {e}", file=sys.stderr)
        return None

