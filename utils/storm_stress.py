"""
Storm Stress Calculation Module
Computes storm severity using ERA5 wind and precipitation data
"""

import numpy as np

def compute_storm_stress(df):
    """
    Calculate storm stress from ERA5 data.
    
    Formula based on wind-load and disaster studies:
    - Wind speed computed from u and v components
    - Gust proxy estimated as 1.3x wind speed (ERA5 doesn't provide gusts directly)
    - Storm stress = gust_proxy² + (precipitation × 10)
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with ERA5 data containing:
        - 10m_u_component_of_wind
        - 10m_v_component_of_wind
        - total_precipitation
    
    Returns:
    --------
    pd.DataFrame
        Original DataFrame with added columns:
        - wind_speed
        - gust_proxy
        - storm_stress
    """
    # Calculate wind speed from u and v components
    df["wind_speed"] = np.sqrt(
        df["10m_u_component_of_wind"] ** 2 +
        df["10m_v_component_of_wind"] ** 2
    )
    
    # Gust proxy (ERA5 does not give gust directly)
    # Factor of 1.3 is commonly used in meteorological studies
    df["gust_proxy"] = df["wind_speed"] * 1.3
    
    # Storm Stress Formula (scientifically defensible)
    # Wind load is proportional to velocity squared
    # Precipitation adds additional stress factor
    df["storm_stress"] = (df["gust_proxy"] ** 2) + (df["total_precipitation"] * 10)
    
    return df


def classify_risk(avg_stress):
    """
    Classify risk zone based on average storm stress.
    
    Parameters:
    -----------
    avg_stress : float
        Average storm stress value
    
    Returns:
    --------
    tuple
        (risk_level, color, description)
    """
    if avg_stress > 2500:
        return ("HIGH", "red", "⚠️ Severe cyclone risk - Immediate evacuation recommended")
    elif avg_stress > 1500:
        return ("MODERATE", "orange", "⚡ Moderate cyclone risk - Stay alert and prepare")
    else:
        return ("LOW", "green", "✅ Low cyclone risk - Normal precautions advised")


def get_stress_statistics(df):
    """
    Get comprehensive stress statistics.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with computed storm_stress column
    
    Returns:
    --------
    dict
        Statistics dictionary
    """
    return {
        "mean": df["storm_stress"].mean(),
        "max": df["storm_stress"].max(),
        "min": df["storm_stress"].min(),
        "std": df["storm_stress"].std(),
        "median": df["storm_stress"].median(),
        "percentile_90": df["storm_stress"].quantile(0.90),
        "percentile_95": df["storm_stress"].quantile(0.95)
    }
