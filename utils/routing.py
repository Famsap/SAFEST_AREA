"""
Routing Module
Calculates optimal evacuation routes using OSRM
"""

import requests
import math

def get_fastest_route(src, dst):
    """
    Get the fastest driving route between two points using OSRM.
    
    Parameters:
    -----------
    src : tuple
        Source coordinates (latitude, longitude)
    dst : tuple
        Destination coordinates (latitude, longitude)
    
    Returns:
    --------
    dict
        Route information including:
        - distance (meters)
        - duration (seconds)
        - geometry (GeoJSON)
    """
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{src[1]},{src[0]};{dst[1]},{dst[0]}"
        f"?overview=full&geometries=geojson"
    )
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("code") == "Ok" and data.get("routes"):
            return data["routes"][0]
        else:
            return None
            
    except requests.RequestException as e:
        print(f"Routing error: {e}")
        return None


def get_multiple_routes(src, destinations):
    """
    Get routes to multiple destinations and rank by travel time.
    
    Parameters:
    -----------
    src : tuple
        Source coordinates (latitude, longitude)
    destinations : list
        List of dictionaries with 'latitude', 'longitude', and other info
    
    Returns:
    --------
    list
        List of route dictionaries sorted by duration
    """
    routes = []
    
    for dest in destinations:
        route = get_fastest_route(
            src,
            (dest["latitude"], dest["longitude"])
        )
        
        if route:
            routes.append({
                "destination": dest,
                "distance_km": route["distance"] / 1000,
                "duration_min": route["duration"] / 60,
                "geometry": route["geometry"]
            })
    
    # Sort by travel time
    routes.sort(key=lambda x: x["duration_min"])
    
    return routes


def calculate_distance(coord1, coord2):
    """
    Calculate approximate distance between two coordinates (Haversine formula).
    
    Parameters:
    -----------
    coord1 : tuple
        First coordinates (latitude, longitude)
    coord2 : tuple
        Second coordinates (latitude, longitude)
    
    Returns:
    --------
    float
        Distance in kilometers
    """
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return c * r
