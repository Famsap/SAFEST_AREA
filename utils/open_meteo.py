"""
Open-Meteo Data Fetch Module
Fetches real-time weather data (Wind, Rain) from Open-Meteo API.
No API Key required.
"""

import requests

def fetch_realtime_weather(lat, lon):
    """
    Fetch current weather conditions for a specific location.
    
    Parameters:
    -----------
    lat : float
        Latitude
    lon : float
        Longitude
    
    Returns:
    --------
    dict
        Dictionary containing:
        - wind_speed (km/h)
        - precipitation (mm)
        - weather_code (int)
        - is_day (int)
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["wind_speed_10m", "precipitation", "weather_code", "is_day", "wind_gusts_10m"],
            "wind_speed_unit": "kmh",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        
        return {
            "wind_speed": current.get("wind_speed_10m", 0),
            "wind_gust": current.get("wind_gusts_10m", 0),
            "precipitation": current.get("precipitation", 0),
            "weather_code": current.get("weather_code", 0),
            "time": current.get("time", "")
        }
        
    except Exception as e:
        print(f"Error fetching Open-Meteo data: {e}")
        # Return safe fallback values if API fails (so app doesn't crash)
        return {
            "wind_speed": 0,
            "wind_gust": 0,
            "precipitation": 0,
            "weather_code": 0,
            "time": "N/A"
        }
