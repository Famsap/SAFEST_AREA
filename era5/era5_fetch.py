"""
ERA5 Data Fetch Module
Fetches real ERA5 reanalysis data from Copernicus Climate Data Store
"""

import cdsapi
import pandas as pd
import os
from dotenv import load_dotenv

def fetch_era5(lat, lon):
    """
    Fetch ERA5 reanalysis data for a specific location.
    
    Parameters:
    -----------
    lat : float
        Latitude of the location
    lon : float
        Longitude of the location
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing wind components and precipitation data
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials
    url = os.getenv("CDSAPI_URL")
    key = os.getenv("CDSAPI_KEY")
    
    if not url or not key:
        print("Warning: CDS API credentials not found in .env file. Checking default location...")
        c = cdsapi.Client() # Fallback to default behavior
    else:
        c = cdsapi.Client(url=url, key=key)

    # Create cache directory if it doesn't exist
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    filename = os.path.join(cache_dir, f"era5_{lat}_{lon}.csv")

    # Return cached data if exists
    if os.path.exists(filename):
        return pd.read_csv(filename)

    # Fetch from ERA5 CDS API
    c.retrieve(
        "reanalysis-era5-single-levels-timeseries",
        {
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "total_precipitation"
            ],
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "date": ["2019-01-01/2024-12-31"],
            "time": [
                "00:00", "06:00", "12:00", "18:00"
            ],
            "data_format": "csv"
        },
        filename
    )

    return pd.read_csv(filename)


def fetch_era5_mock(lat, lon):
    """
    Mock ERA5 data for testing without CDS API.
    Uses realistic cyclone-prone region data patterns.
    
    This is useful for development/demo when CDS API is not configured.
    """
    import numpy as np
    
    # Generate realistic mock data for 5 years
    dates = pd.date_range(start='2019-01-01', end='2024-12-31', freq='6H')
    
    # Base wind patterns (seasonal variation for cyclone-prone regions)
    month_factor = np.sin(np.array([d.month for d in dates]) * np.pi / 6)
    
    # Random variations
    np.random.seed(int(abs(lat * 100 + lon * 10)) % 10000)
    
    # U-component of wind (m/s): typical 5-25 m/s during cyclones
    u_base = 8 + 5 * month_factor + np.random.normal(0, 3, len(dates))
    
    # V-component of wind (m/s)
    v_base = 6 + 4 * month_factor + np.random.normal(0, 2.5, len(dates))
    
    # Total precipitation (m): higher during monsoon
    precip = np.abs(0.001 + 0.003 * month_factor + np.random.exponential(0.002, len(dates)))
    
    # Add some extreme events (cyclones)
    extreme_indices = np.random.choice(len(dates), size=50, replace=False)
    u_base[extreme_indices] *= 2.5
    v_base[extreme_indices] *= 2.3
    precip[extreme_indices] *= 5
    
    df = pd.DataFrame({
        'datetime': dates,
        '10m_u_component_of_wind': u_base,
        '10m_v_component_of_wind': v_base,
        'total_precipitation': precip
    })
    
    return df
