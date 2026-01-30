"""
Extract historical cyclone events from IBTrACS database for Odisha region.

This module:
1. Downloads IBTrACS cyclone database
2. Filters for North Indian Ocean basin
3. Extracts cyclones affecting Odisha (lat/lon bounds)
4. Aggregates each cyclone into single event
5. Outputs: data/regions/odisha/cyclone_events.csv
"""

import pandas as pd
import requests
import os
from datetime import datetime

# Odisha geographic bounds
ODISHA_BOUNDS = {
    'lat_min': 17.78,
    'lat_max': 22.57,
    'lon_min': 81.37,
    'lon_max': 87.53
}

IBTRACS_URL = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/csv/ibtracs.NI.list.v04r00.csv"

def download_ibtracs():
    """Download IBTrACS database for North Indian Ocean."""
    print("Downloading IBTrACS database...")
    response = requests.get(IBTRACS_URL, timeout=120)
    response.raise_for_status()
    
    # Save to temp file
    temp_file = "ibtracs_temp.csv"
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    print(f"Downloaded {len(response.content) / 1024 / 1024:.2f} MB")
    return temp_file

def filter_odisha_cyclones(ibtracs_file):
    """Filter cyclones that affected Odisha region."""
    print("Loading IBTrACS data...")
    
    # Read with proper handling of header rows
    df = pd.read_csv(ibtracs_file, skiprows=[1], low_memory=False)
    
    print(f"Total records: {len(df)}")
    
    # Filter for North Indian Ocean basin
    df = df[df['BASIN'] == 'NI'].copy()
    print(f"North Indian Ocean records: {len(df)}")
    
    # Convert lat/lon to numeric
    df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
    df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
    df['WMO_WIND'] = pd.to_numeric(df['WMO_WIND'], errors='coerce')
    
    # Filter for Odisha bounds
    odisha_mask = (
        (df['LAT'] >= ODISHA_BOUNDS['lat_min']) &
        (df['LAT'] <= ODISHA_BOUNDS['lat_max']) &
        (df['LON'] >= ODISHA_BOUNDS['lon_min']) &
        (df['LON'] <= ODISHA_BOUNDS['lon_max'])
    )
    
    df_odisha = df[odisha_mask].copy()
    print(f"Odisha-affecting records: {len(df_odisha)}")
    
    return df_odisha

def aggregate_cyclone_events(df):
    """Aggregate each cyclone into single event with max intensity."""
    print("Aggregating cyclone events...")
    
    # Group by storm ID and aggregate
    events = df.groupby('SID').agg({
        'ISO_TIME': 'first',  # First timestamp
        'LAT': 'mean',  # Average position
        'LON': 'mean',
        'WMO_WIND': 'max',  # Maximum wind speed
        'NAME': 'first'
    }).reset_index()
    
    # Rename columns
    events.columns = ['event_id', 'timestamp', 'lat', 'lon', 'max_wind_speed', 'name']
    
    # Convert wind speed from knots to km/h
    events['max_wind_speed'] = events['max_wind_speed'] * 1.852
    
    # Filter out events with missing wind data
    events = events.dropna(subset=['max_wind_speed'])
    
    # Sort by timestamp
    events['timestamp'] = pd.to_datetime(events['timestamp'])
    events = events.sort_values('timestamp')
    
    print(f"Total cyclone events: {len(events)}")
    print(f"Date range: {events['timestamp'].min()} to {events['timestamp'].max()}")
    
    return events

def main():
    """Main execution function."""
    print("=" * 60)
    print("PHASE A.1: Extract IBTrACS Cyclone History for Odisha")
    print("=" * 60)
    
    # Create output directory
    output_dir = "data/regions/odisha"
    os.makedirs(output_dir, exist_ok=True)
    
    # Download IBTrACS data
    ibtracs_file = download_ibtracs()
    
    # Filter for Odisha
    df_odisha = filter_odisha_cyclones(ibtracs_file)
    
    # Aggregate events
    events = aggregate_cyclone_events(df_odisha)
    
    # Save output
    output_file = os.path.join(output_dir, "cyclone_events.csv")
    events.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Display sample
    print("\nSample events:")
    print(events.head(10).to_string())
    
    # Clean up temp file
    if os.path.exists(ibtracs_file):
        os.remove(ibtracs_file)
    
    print("\n" + "=" * 60)
    print("PHASE A.1 COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
