import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.routing import get_fastest_route, calculate_distance
from utils.storm_stress import classify_risk
from utils.open_meteo import fetch_realtime_weather

# Page configuration
st.set_page_config(
    page_title="CycloneSafeRoute",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AESTHETIC CSS & ANIMATIONS ---
st.markdown("""
<style>
    /* 1. ANIMATIONS */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes pulseBlue {
        0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(37, 99, 235, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }

    /* 2. GLOBAL THEME (Professional White) */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #1e293b; /* Slate 800 */
    }
    
    /* Main Background */
    .stApp {
        background-color: #f8fafc; /* Very light blue-grey */
        background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
        background-size: 24px 24px;
    }

    /* 3. HEADER STYLE */
    .aesthetic-header {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 1);
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
        animation: fadeIn 1s ease-out;
    }
    
    .aesthetic-header h1 {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .aesthetic-header p {
        color: #64748b;
        font-size: 1.1rem;
        margin-top: 0.8rem;
        font-weight: 400;
    }

    /* 4. CARDS & CONTAINERS */
    .glass-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: slideUp 0.6s ease-out;
        margin-bottom: 1rem;
    }
    
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
        border-color: #e2e8f0;
    }
    
    .metric-title {
        color: #64748b; /* Slate 500 */
        font-size: 0.8rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .metric-value {
        color: #0f172a; /* Slate 900 */
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    /* 5. SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* 6. BUTTONS */
    .stButton>button {
        background: #2563eb; /* Royal Blue */
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        background: #1d4ed8;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }

    /* 7. RISK BADGES */
    .risk-badge-soft {
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    /* 8. GENERAL TEXT OVERRIDES */
    h3 {
        color: #1e293b !important;
        font-weight: 600;
    }
    
    .stMarkdown p {
        color: #475569;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div class="aesthetic-header">
    <h1>🌪️ CycloneSafeRoute</h1>
    <p>AI-Powered Disaster Analytics & Safe Path Navigation</p>
</div>
""", unsafe_allow_html=True)

# Load Camps
@st.cache_data
def load_camps():
    return pd.read_csv("data/relief_camps.csv")

camps = load_camps()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Google_Maps_icon.svg/512px-Google_Maps_icon.svg.png", width=60)
    st.markdown("### 🍃 Navigation")
    
    # Simple aesthetic toggle
    st.markdown("**(1) Location Source**")
    
    # Automatic Geolocation
    loc = get_geolocation(component_key="live_location")
    
    if loc and "coords" in loc:
        lat = loc["coords"]["latitude"]
        lon = loc["coords"]["longitude"]
        
        if "location_source" not in st.session_state or st.session_state["location_source"] == "gps":
            st.session_state["user_location"] = (lat, lon)
            st.session_state["location_source"] = "gps"
            # Reset route if location changes
            if "current_route" in st.session_state:
                del st.session_state["current_route"]
            st.success(f"📍 GPS Active")

    st.info("Click anywhere on the map to set a custom location.")
    
    st.markdown("---")
    st.markdown("**Status**")
    st.caption("🟢 Meteo API: Connected")
    st.caption("🟢 Routing Engine: Ready")

# --- STATE MANAGEMENT ---
if "user_location" not in st.session_state:
    st.session_state["user_location"] = None
if "location_source" not in st.session_state:
    st.session_state["location_source"] = "init"
if "current_route" not in st.session_state:
    st.session_state["current_route"] = None

# --- MAIN LAYOUT ---
col_map, col_details = st.columns([1.6, 1], gap="medium")

with col_map:
    st.markdown("### 🗺️ Live Territory Map")
    
    # Default Center (Odisha)
    default_lat, default_lon = 20.2961, 85.8245
    start_loc = st.session_state["user_location"] if st.session_state["user_location"] else [default_lat, default_lon]
    
    # Aesthetic Light Map Tiles (Professional Style)
    m = folium.Map(location=start_loc, zoom_start=8, tiles="CartoDB positron")
    
    # Styles
    for _, camp in camps.iterrows():
        folium.Marker(
            [camp["latitude"], camp["longitude"]],
            popup=f"<b>{camp['camp_name']}</b><br>Capacity: {camp['capacity']}",
            icon=folium.Icon(color="green", icon="home", prefix="fa") # Green Home = Safety (Google Style)
        ).add_to(m)

    if st.session_state["user_location"]:
        u_lat, u_lon = st.session_state["user_location"]
        folium.Marker(
            [u_lat, u_lon],
            popup="📍 You are here",
            icon=folium.Icon(color="red", icon="map-marker", prefix="fa"), # Red Pin = Google Maps Current Loc
        ).add_to(m)
        
        # Display Route if calculated
        if st.session_state["current_route"]:
            folium.GeoJson(
                st.session_state["current_route"]["geometry"],
                style_function=lambda x: {"color": "#2563eb", "weight": 5, "opacity": 0.8} # Royal Blue
            ).add_to(m)

    # MAP OUTPUT
    map_output = st_folium(m, height=550, width=None)

    if map_output["last_clicked"]:
        clicked_lat = map_output["last_clicked"]["lat"]
        clicked_lon = map_output["last_clicked"]["lng"]
        
        # Only update if changed
        if st.session_state["user_location"] != (clicked_lat, clicked_lon):
            st.session_state["user_location"] = (clicked_lat, clicked_lon)
            st.session_state["location_source"] = "manual"
            # Reset route
            st.session_state["current_route"] = None
            st.rerun()

# --- DETAILS PANEL ---
with col_details:
    st.markdown("### 📊 Live Analytics")
    
    if st.session_state["user_location"]:
        u_lat, u_lon = st.session_state["user_location"]
        
        # Skeleton loader animation effect
        with st.spinner("Processing satellite data..."):
            time.sleep(0.5) # Fake small delay to show off spinner animation
            weather = fetch_realtime_weather(u_lat, u_lon)
        
        # Risk Calc
        storm_stress = (weather['wind_speed'] ** 2) + (weather['precipitation'] * 10)
        risk_level, risk_color, risk_msg = classify_risk(storm_stress)
        
        # 1. WEATHER CARDS
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="glass-card">
                <div class="metric-title">Wind Speed</div>
                <div class="metric-value">{weather['wind_speed']} <span style="font-size:1rem;color:#b2bec3;">km/h</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="glass-card">
                <div class="metric-title">Rainfall</div>
                <div class="metric-value">{weather['precipitation']} <span style="font-size:1rem;color:#b2bec3;">mm</span></div>
            </div>
            """, unsafe_allow_html=True)

        # 2. RISK CARD
        # Professional colors for risk (Light Mode)
        if risk_level == "HIGH":
            bg_col = "#fee2e2" # Light Red
            border_col = "#ef4444"
            txt_col = "#b91c1c"
        elif risk_level == "MODERATE":
            bg_col = "#ffedd5" # Light Orange
            border_col = "#f97316"
            txt_col = "#c2410c"
        else:
            bg_col = "#dcfce7" # Light Green
            border_col = "#22c55e"
            txt_col = "#15803d"
        
        st.markdown(f"""
        <div class="risk-badge-soft" style="background-color: {bg_col}; color: {txt_col}; border: 1px solid {border_col};">
            Creating Risk Profile: {risk_level}
        </div>
        <p style="text-align:center; font-size:0.9rem; color:#64748b; margin-top:10px;"><em>{risk_msg}</em></p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 3. ROUTING
        nearest_camp = None
        min_dist = float('inf')
        
        for _, camp in camps.iterrows():
            d = calculate_distance((u_lat, u_lon), (camp["latitude"], camp["longitude"]))
            if d < min_dist:
                min_dist = d
                nearest_camp = camp
        
        if nearest_camp is not None:
             st.markdown("#### 🛡️ Nearest Safe Sanctuary")
             st.markdown(f"""
             <div class="glass-card" style="border-left: 4px solid #2563eb;">
                <h3 style="margin:0; color:#1e293b; font-size:1.4rem;">{nearest_camp['camp_name']}</h3>
                <p style="color:#64748b; margin-bottom:15px; font-size:0.9rem;">Secure Facility • <span style="color:#2563eb; font-weight:600;">{nearest_camp['capacity']} Spots Available</span></p>
                <div style="display:flex; justify-content:space-between; color:#3b82f6; font-weight:600; margin-top:10px;">
                    <span>📍 {min_dist:.1f} km away</span>
                </div>
             </div>
             """, unsafe_allow_html=True)
             
             if st.button("Draw Evacuation Path"):
                 route = get_fastest_route((u_lat, u_lon), (nearest_camp["latitude"], nearest_camp["longitude"]))
                 
                 if route:
                    t_mins = route['duration']/60
                    st.session_state["current_route"] = route
                    st.success(f"Route Calculated: {t_mins:.0f} mins travel time")
                    st.rerun() # Rerun to update map
                 else:
                     st.error("Could not calculate route. Service may be unavailable.")
                     
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📍</div>
            <h3 style="color:#636e72;">Waiting for location...</h3>
            <p style="color:#b2bec3;">Click "Use GPS" or Select on Map</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<br><br>
<div style="text-align: center; color: #b2bec3; font-size: 0.8rem;">
    CycloneSafeRoute • Designed for Safety
</div>
""", unsafe_allow_html=True)
