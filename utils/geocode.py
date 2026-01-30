"""
Geocoding Module
Converts city names to latitude/longitude coordinates
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_coordinates(city, country="India"):
    """
    Get latitude and longitude for a city.
    
    Parameters:
    -----------
    city : str
        Name of the city
    country : str
        Country name (default: India)
    
    Returns:
    --------
    tuple
        (latitude, longitude) or (None, None) if not found
    """
    try:
        geo = Nominatim(user_agent="cyclone_safe_route_app")
        location = geo.geocode(f"{city}, {country}", timeout=10)
        
        if location:
            return location.latitude, location.longitude
        return None, None
        
    except GeocoderTimedOut:
        print(f"Geocoding timed out for {city}")
        return None, None
    except GeocoderServiceError as e:
        print(f"Geocoding service error: {e}")
        return None, None


def get_city_info(city, country="India"):
    """
    Get detailed location information for a city.
    
    Parameters:
    -----------
    city : str
        Name of the city
    country : str
        Country name (default: India)
    
    Returns:
    --------
    dict
        Location information or None if not found
    """
    try:
        geo = Nominatim(user_agent="cyclone_safe_route_app")
        location = geo.geocode(f"{city}, {country}", timeout=10, addressdetails=True)
        
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address,
                "raw": location.raw
            }
        return None
        
    except Exception as e:
        print(f"Error getting city info: {e}")
        return None


# Pre-defined coordinates for common cyclone-prone cities in India
CYCLONE_CITIES = {
    "puri": (19.8135, 85.8312),
    "bhubaneswar": (20.2961, 85.8245),
    "cuttack": (20.4625, 85.8830),
    "visakhapatnam": (17.6868, 83.2185),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "mumbai": (19.0760, 72.8777),
    "paradip": (20.3164, 86.6085),
    "gopalpur": (19.2594, 84.9058),
    "machilipatnam": (16.1875, 81.1389),
    "kakinada": (16.9891, 82.2475),
    "porbandar": (21.6417, 69.6293),
    "veraval": (20.9073, 70.3626),
    "digha": (21.6283, 87.5120)
}

def get_coordinates_fast(city, country="India"):
    """
    Get coordinates with fallback to pre-defined cities.
    Faster than geocoding for common cyclone-prone areas.
    
    Parameters:
    -----------
    city : str
        Name of the city
    country : str
        Country name (default: India)
    
    Returns:
    --------
    tuple
        (latitude, longitude) or (None, None) if not found
    """
    # Check pre-defined cities first
    city_lower = city.lower().strip()
    if city_lower in CYCLONE_CITIES:
        return CYCLONE_CITIES[city_lower]
    
    # Fallback to geocoding
    return get_coordinates(city, country)
