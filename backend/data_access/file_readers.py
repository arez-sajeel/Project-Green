# backend/data_access/file_readers.py

# This file implements the base drivers for reading local files (CSV/JSON),
# as specified in Task 1.b.
# This adheres to the "Modularity (Data Access Layer)" coding standard.
# It uses pandas for efficient file parsing.
# ---
# MODIFIED FOR SPRINT 2 (Task 2.2):
# - Added 'load_and_simulate_ukpn_data' to fulfill FR2.3 and FR2.5
#   by loading, transforming, and simulating portfolio data.
# ---

import csv
import sys
from datetime import datetime
import pandas as pd  

from typing import List, Dict, Any, Optional

from models.usage import HistoricalUsageLog   


# Per P3, a custom error for clarity
class DataLoadError(Exception):
    """Custom exception for data loading failures."""
    pass

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
    
    NOTE: This function is now superseded by the more specific
    'load_and_simulate_ukpn_data' for Task 2.2, but is kept
    for potential testing or other uses.
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

# --- NEW (Sprint 2): Task 2.2 Core Logic ---

def load_and_simulate_ukpn_data(
    file_path: str
) -> List[HistoricalUsageLog]:
    """
    Loads historical data from the UKPN file (Task 2.2),
    simulates portfolio groupings (FR2.3), and maps
    the data to the HistoricalUsageLog Pydantic model (FR2.5).
    
    This implementation prioritizes readability (P2) and
    explicit error handling (P3 / NFR-S3).
    """
    
    print(f"Task 2.2: Attempting to load and simulate data from: {file_path}...", file=sys.stdout)

    # P3: All data processing must be in a try/except block
    try:
        # 1. Read the local data file
        # We assume the file is a CSV as per the S1 Data Access task
        df = pd.read_csv(file_path)
        
        # --- Data Cleaning & Renaming (Clarity P2) ---
        # Rename columns to match our database schema.
        # This keeps our logic clear and avoids confusion.
        # We assume the CSV has columns: 'Meter_ID', 'Timestamp', 'Consumption_kWh'
        df.rename(columns={
            'Meter_ID': 'mpan_id',
            'Timestamp': 'timestamp',
            'Consumption_kWh': 'kwh_consumption'
        }, inplace=True)
        
        # Ensure timestamp is a proper datetime object for Pydantic
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # --- Simulate Portfolios (FR2.3) ---
        # We need to assign a portfolio_id to each meter to satisfy
        # the PropertyManager (FR2.4) and Access Control (NFR-S2) requirements.
        
        # We'll use a simple, clear, and fast 'map' method.
        # First, get all unique meter IDs
        unique_mpans = df['mpan_id'].unique()
        
        # Second, create a mapping: {mpan_id -> portfolio_id}
        # We'll group them into portfolios of 100 meters each.
        portfolio_map = {
            mpan: f"sim_portfolio_{(i // 100) + 1}" 
            for i, mpan in enumerate(unique_mpans)
        }
        
        # Third, apply this map to the DataFrame to create the new column
        df['portfolio_id'] = df['mpan_id'].map(portfolio_map)
        
        # --- Map to Pydantic Model (FR2.5) ---
        
        # Add the remaining fields required by the HistoricalUsageLog model
        
        # kwh_cost will be calculated in Sprint 3. For now, it's 0.0.
        df['kwh_cost'] = 0.0
        
        # 'S' stands for 'Simulated' (supports NFR-S3)
        df['reading_type'] = 'S'
        
        # Drop any rows that might have failed (e.g., bad data)
        df.dropna(subset=[
            'timestamp', 'mpan_id', 'portfolio_id', 'kwh_consumption'
        ], inplace=True)

        # Convert the clean DataFrame to a list of dictionaries
        data_dicts = df.to_dict(orient='records')
        
        # Use a simple list comprehension to validate data with Pydantic
        # This is fast and ensures data integrity.
        models = [HistoricalUsageLog(**data) for data in data_dicts]
        
        print(f"Task 2.2: Successfully loaded and simulated {len(models)} log entries.", file=sys.stdout)
        return models

    except FileNotFoundError:
        print(f"Error (Task 2.2): Data file not found at {file_path}", file=sys.stderr)
        raise DataLoadError(f"File not found: {file_path}")
    except KeyError as e:
        print(f"Error (Task 2.2): Missing expected column in CSV: {e}", file=sys.stderr)
        raise DataLoadError(f"Missing column {e} in {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred in Task 2.2: {e}", file=sys.stderr)
        raise DataLoadError(f"An unexpected error occurred: {e}")
