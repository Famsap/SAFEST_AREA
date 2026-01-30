"""
Extract ERA5 reanalysis weather data for historical cyclone events.

This module:
1. Reads cyclone events from IBTrACS output
2. Queries ERA5 reanalysis for actual weather during events
3. Computes: max wind speed, max gust speed, total rainfall
4. Outputs: data/regions/odisha/era5_weather.csv

Note: For demo purposes, this uses synthetic ERA5-like data.
In production, use cdsapi to fetch real ERA5 data.
"""

import pandas as pd
import numpy as np
import os

def load_cyclone_events():
    """Load cyclone events from IBTrACS extraction."""
    events_file = "data/regions/odisha/cyclone_events.csv"
    
    if not os.path.exists(events_file):
        raise FileNotFoundError(
            f"Cyclone events file not found: {events_file}\n"
            "Run extract_ibtracs.py first."
        )
    
    events = pd.read_csv(events_file)
    events['timestamp'] = pd.to_datetime(events['timestamp'])
    
    print(f"Loaded {len(events)} cyclone events")
    return events

def fetch_era5_data(event):
    """
    Fetch ERA5 reanalysis data for a cyclone event.
    
    In production, this would use cdsapi:
    ```python
    import cdsapi
    c = cdsapi.Client()
    c.retrieve('reanalysis-era5-single-levels', {
        'product_type': 'reanalysis',
        'variable': ['10m_u_component_of_wind', '10m_v_component_of_wind', 'total_precipitation'],
        'date': event_date,
        'area': [lat_max, lon_min, lat_min, lon_max],
    }, 'output.nc')
    ```
    
    For demo, we generate synthetic but realistic data based on IBTrACS wind speeds.
    """
    
    # Use IBTrACS wind as baseline
    base_wind = event['max_wind_speed']
    
    # ERA5 typically shows slightly lower winds than best track (surface vs flight level)
    # Add realistic variability
    max_wind_speed = base_wind * np.random.uniform(0.85, 0.95)
    
    # Gust factor typically 1.2-1.5x sustained wind
    max_gust_speed = max_wind_speed * np.random.uniform(1.2, 1.5)
    
    # Rainfall correlates with intensity but has high variance
    # Typical cyclone: 100-400mm, intense: 400-800mm
    if base_wind > 150:  # Severe cyclone
        total_rainfall = np.random.uniform(300, 700)
    elif base_wind > 100:  # Moderate cyclone
        total_rainfall = np.random.uniform(150, 400)
    else:  # Weak cyclone
        total_rainfall = np.random.uniform(50, 200)
    
    return {
        'max_wind_speed': max_wind_speed,
        'max_gust_speed': max_gust_speed,
        'total_rainfall': total_rainfall
    }

def extract_weather_for_all_events(events):
    """Extract ERA5 weather data for all cyclone events."""
    print("Extracting ERA5 weather data...")
    
    weather_data = []
    
    for idx, event in events.iterrows():
        print(f"Processing event {idx + 1}/{len(events)}: {event['name']} ({event['timestamp'].year})")
        
        weather = fetch_era5_data(event)
        
        weather_data.append({
            'event_id': event['event_id'],
            'name': event['name'],
            'timestamp': event['timestamp'],
            'max_wind_speed': weather['max_wind_speed'],
            'max_gust_speed': weather['max_gust_speed'],
            'total_rainfall': weather['total_rainfall']
        })
    
    return pd.DataFrame(weather_data)

def main():
    """Main execution function."""
    print("=" * 60)
    print("PHASE A.2: Extract ERA5 Weather Data")
    print("=" * 60)
    
    # Load cyclone events
    events = load_cyclone_events()
    
    # Extract weather data
    weather_df = extract_weather_for_all_events(events)
    
    # Save output
    output_file = "data/regions/odisha/era5_weather.csv"
    weather_df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Display statistics
    print("\nWeather Statistics:")
    print(weather_df[['max_wind_speed', 'max_gust_speed', 'total_rainfall']].describe())
    
    print("\n" + "=" * 60)
    print("PHASE A.2 COMPLETE")
    print("=" * 60)
    print("\nNote: This demo uses synthetic ERA5-like data.")
    print("For production, integrate real ERA5 API using cdsapi.")

if __name__ == "__main__":
    main()
