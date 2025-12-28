# app.py - PART 1
# Green Rooftop Analyzer - Enhanced Futuristic UI
# Save this as app.py and combine with Part 2

import streamlit as st
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime

# Import modules
from models.roof_segmentation import SimplifiedRoofSegmenter
from models.feature_extractor import RoofFeatureExtractor
from utils.api_integrations import WeatherAPI, LocationAPI, GeminiAPI
from utils.calculations import (
    SolarCalculator, RainwaterCalculator, 
    GardeningCalculator, EnvironmentalImpact
)

# Page config
st.set_page_config(
    page_title="Green Rooftop Analyzer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Enhanced CSS with futuristic design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        background-attachment: fixed;
    }
    
    /* All text color fixes */
    p, span, div, label {
        color: #e0e0e0 !important;
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00ff87, #60efff, #00ff87);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 255, 135, 0.5);
        margin-bottom: 0.5rem;
        animation: glow 2s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        text-align: center;
        color: #60efff !important;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 31, 58, 0.9), rgba(15, 20, 25, 0.9));
        border: 1px solid rgba(0, 255, 135, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 255, 135, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(0, 255, 135, 0.8);
        box-shadow: 0 8px 32px rgba(0, 255, 135, 0.3);
        transform: translateY(-5px);
    }
    
    .metric-card h4, .metric-card p {
        color: #ffffff !important;
    }
    
    .score-excellent {
        color: #00ff87 !important;
        font-weight: bold;
        font-size: 1.8rem;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(0, 255, 135, 0.8);
    }
    
    .score-good {
        color: #ffd700 !important;
        font-weight: bold;
        font-size: 1.8rem;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
    }
    
    .score-fair {
        color: #ff6b6b !important;
        font-weight: bold;
        font-size: 1.8rem;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(255, 107, 107, 0.8);
    }
    
    .weather-widget {
        background: linear-gradient(135deg, rgba(96, 239, 255, 0.1), rgba(0, 255, 135, 0.1));
        border: 1px solid rgba(96, 239, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .weather-widget * {
        color: #ffffff !important;
    }
    
    .weather-temp {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        color: #60efff !important;
        text-shadow: 0 0 10px rgba(96, 239, 255, 0.5);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00ff87, #60efff);
        color: #0a0e27 !important;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 255, 135, 0.8);
        transform: scale(1.05);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: #00ff87 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(26, 31, 58, 0.5);
        border-radius: 10px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(0, 255, 135, 0.1);
        border: 1px solid rgba(0, 255, 135, 0.3);
        border-radius: 8px;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(0, 255, 135, 0.3), rgba(96, 239, 255, 0.3));
        border-color: #00ff87;
        color: #ffffff !important;
    }
    
    .info-box {
        background: rgba(0, 255, 135, 0.1);
        border-left: 4px solid #00ff87;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .info-box * {
        color: #ffffff !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #0f1419 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        color: #60efff !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00ff87 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: #ffffff !important;
        background: rgba(0, 255, 135, 0.1);
        border-radius: 8px;
    }
    
    /* Small text */
    small {
        color: #b0b0b0 !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] label {
        color: #ffffff !important;
    }
</style>
            
""", unsafe_allow_html=True)
def get_city_name(loc_data):
    """Safely extract city/town name — handles strings, None, and malformed dicts"""
    # Handle None, string, or invalid data
    if not loc_data or isinstance(loc_data, str):
        return "Unknown City"
    
    if not isinstance(loc_data, dict):
        return "Unknown City"
    
    # Try direct keys
    for key in ['city', 'town', 'village', 'county', 'municipality', 'state_district', 'suburb']:
        if loc_data.get(key):
            return loc_data[key]
    
    # Try inside 'address' dict safely
    address = loc_data.get('address', {})
    if isinstance(address, dict):
        for key in ['city', 'town', 'village', 'county', 'municipality']:
            if address.get(key):
                return address[key]
    
    # Fallback: use display_name first part
    display = loc_data.get('display_name', '')
    if display and ',' in display:
        return display.split(',')[0].strip()
    
    # Final fallback
    return loc_data.get('name', 'Unknown City')

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'ml_features' not in st.session_state:
        st.session_state.ml_features = None
    if 'gemini_results' not in st.session_state:
        st.session_state.gemini_results = None
    if 'location_data' not in st.session_state:
        st.session_state.location_data = None
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = None


@st.cache_resource
def load_models():
    """Load ML models (cached)"""
    try:
        segmenter = SimplifiedRoofSegmenter()
        extractor = RoofFeatureExtractor()
        return segmenter, extractor
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None


def analyze_rooftop(image, location_data):
    """Complete rooftop analysis pipeline"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Segmentation
    status_text.text("🔍 Analyzing roof structure...")
    progress_bar.progress(25)
    segmenter, extractor = load_models()
    seg_result = segmenter.segment_roof(image)
    st.session_state.seg_result = seg_result
    
    # Step 2: Feature extraction
    status_text.text("🔬 Extracting features...")
    progress_bar.progress(50)
    features = extractor.extract_all_features(image, seg_result.get('roof_mask'))
    ml_features = {**seg_result, **features}
    st.session_state.ml_features = ml_features
    
    # Step 3: Weather data
    status_text.text("🌤️ Fetching weather data...")
    progress_bar.progress(75)
    weather_api = WeatherAPI()
    weather_data = weather_api.get_weather_data(location_data['lat'], location_data['lon'])
    st.session_state.weather_data = weather_data
    
    # Step 4: AI analysis
    status_text.text("🤖 Running AI analysis...")
    progress_bar.progress(90)
    
    try:
        gemini_api = GeminiAPI()
        gemini_results = gemini_api.analyze_rooftop(ml_features, weather_data, location_data)
        st.session_state.gemini_results = gemini_results
    except Exception as e:
        st.warning(f"AI Analysis unavailable: {e}")
        gemini_results = generate_fallback_analysis(ml_features, weather_data)
        st.session_state.gemini_results = gemini_results
    
    progress_bar.progress(100)
    status_text.text("✅ Analysis complete!")
    st.session_state.analysis_complete = True
    
    return True


def generate_fallback_analysis(ml_features, weather_data):
    """Generate analysis using local calculators — FULLY COMPATIBLE WITH UI"""
    
    solar_calc = SolarCalculator()
    rain_calc = RainwaterCalculator()
    garden_calc = GardeningCalculator()
    env_calc = EnvironmentalImpact()
    
    usable_area = ml_features.get('usable_area_sqft', 800)
    roof_area = ml_features.get('roof_area_sqft', 1000)
    orientation = ml_features.get('orientation', 'South')
    shading = ml_features.get('shading_percent', 10)
    
    # Solar calculations
    system_size, panel_count = solar_calc.calculate_system_size(usable_area)
    solar_production = solar_calc.calculate_production(
        system_size, weather_data['climate']['solar_irradiance'], shading, orientation
    )
    solar_roi = solar_calc.calculate_roi(system_size, solar_production)
    solar_impact = env_calc.calculate_solar_impact(solar_production)
    
    # Rainwater calculations
    rain_collection = rain_calc.calculate_collection(
        roof_area, weather_data['climate']['annual_rainfall_mm']
    )
    rain_savings = rain_calc.calculate_savings(rain_collection)
    
    # Gardening calculations
    garden_potential = garden_calc.calculate_potential(usable_area)
    
    # Scores
    solar_score = min(10, (usable_area / 100) + (8 if orientation == 'South' else 6))
    rain_score = min(10, (weather_data['climate']['annual_rainfall_mm'] / 100))
    garden_score = min(10, (usable_area * 0.3 / 50) + 5)
    
    # Determine best technology
    scores = {'solar': solar_score, 'rainwater': rain_score, 'gardening': garden_score}
    best_tech = max(scores, key=scores.get)
    
    return {
        "solar": {
            "suitability_score": round(solar_score, 1),
            "system_size_kw": system_size,
            "panel_count": panel_count,
            "annual_production_kwh": solar_production,
            "installation_cost_usd": solar_roi['net_cost'],
            "annual_savings_usd": solar_roi['annual_savings'],
            "payback_years": solar_roi['payback_period'],
            "key_points": [
                f"{orientation}-facing orientation detected",
                f"Can install {panel_count} solar panels",
                f"Expected payback period: {solar_roi['payback_period']} years"
            ],
            "pros": ["Reduces electricity bills significantly", "Low maintenance requirements"],
            "cons": ["High initial investment", f"{shading}% shading may reduce efficiency"],
            "optimization_tips": ["Consider battery storage for excess power", "Regular panel cleaning recommended"]
        },
        "rainwater": {
            "suitability_score": round(rain_score, 1),
            "annual_collection_liters": rain_collection,
            "tank_size_needed_liters": rain_savings['tank_size'],
            "installation_cost_usd": rain_savings['installation_cost'],
            "annual_savings_usd": rain_savings['annual_savings'],
            "water_self_sufficiency_percent": min(100, int(rain_collection / 1000)),
            "key_points": [
                f"Annual collection: {rain_collection:,} liters",
                f"Tank size needed: {rain_savings['tank_size']:,}L",
                f"Payback: {rain_savings['payback_period']} years"
            ],
            "pros": ["Reduces water bills", "Sustainable water source"],
            "cons": ["Requires storage space", "Seasonal availability varies"],
            "usage_recommendations": ["Use for gardening and cleaning", "Install filtration for potable use"]
        },
        "gardening": {
            "suitability_score": round(garden_score, 1),
            "plantable_area_sqft": garden_potential['plantable_area'],
            "recommended_crops": garden_potential['recommended_crops'],
            "annual_yield_kg": garden_potential['annual_yield_kg'],
            "setup_cost_usd": garden_potential['setup_cost'],
            "annual_value_usd": garden_potential['annual_value'],
            "key_points": [
                f"Plantable area: {garden_potential['plantable_area']} sqft",
                f"Expected yield: {garden_potential['annual_yield_kg']} kg/year",
                f"Annual value: ${garden_potential['annual_value']}"
            ],
            "pros": ["Fresh organic produce", "Improves air quality"],
            "cons": ["Requires regular maintenance", "Structural load considerations"],
            "seasonal_tips": ["Rotate crops seasonally", "Use lightweight soil mixes"]
        },
             "overall": {
            "best_technology": best_tech,
            "combined_score": round((solar_score + rain_score + garden_score) / 3, 1),
            "recommendation": f"{best_tech.capitalize()} recommended as primary technology with strong local performance.",
            "implementation_priority": ["Solar Panels", "Rainwater Harvesting", "Rooftop Gardening"],
            "environmental_impact": {
                "co2_offset_tons_per_year": solar_impact['co2_offset_tons'],
                "water_saved_liters_per_year": rain_collection,
                "food_produced_kg_per_year": garden_potential['annual_yield_kg']
            },
            "total_investment_usd": solar_roi['net_cost'] + rain_savings['installation_cost'] + garden_potential['setup_cost'],
            "total_annual_savings_usd": solar_roi['annual_savings'] + rain_savings['annual_savings'] + garden_potential['annual_value']
        }
    }

# END OF PART 1
# Continue with Part 2 for display functions and main()
# app.py - PART 2
# Copy this after Part 1 in your app.py file

def create_weather_widget(weather_data):
    current = weather_data.get('current', {})
    location = weather_data.get('location', {})
    
    location_name = location.get('name', 'Unknown')
    location_country = location.get('country', '')
    
    # FIXED: Only use get_city_name if location_data is a dict
    if location_name == 'Unknown' and st.session_state.location_data and isinstance(st.session_state.location_data, dict):
        loc_data = st.session_state.location_data
        location_name = get_city_name(loc_data)
        location_country = loc_data.get('country', '')
    
    st.markdown(f"""
    <div class="weather-widget">
        <h3 style="color: #60efff; margin: 0;">Current Weather - {location_name}{', ' + location_country if location_country else ''}</h3>
        <div style="display: flex; align-items: center; margin-top: 15px;">
            <div style="flex: 1;">
                <div class="weather-temp">{current.get('temp', 'N/A')}°C</div>
                <div style="color: #00ff87; font-size: 1.2rem;">{current.get('description', 'Loading...')}</div>
            </div>
            <div style="flex: 1; text-align: right;">
                <div style="color: #60efff; font-size: 1rem;">Humidity: {current.get('humidity', 'N/A')}%</div>
                <div style="color: #60efff; font-size: 1rem;">Wind: {current.get('wind_speed', 'N/A')} m/s</div>
                <div style="color: #60efff; font-size: 1rem;">Clouds: {current.get('clouds', 'N/A')}%</div>
            </div>
        </div>
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(96, 239, 255, 0.2);">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #ffd700;">Sunrise: {current.get('sunrise', 'N/A')}</span>
                <span style="color: #ff6b6b;">Sunset: {current.get('sunset', 'N/A')}</span>
                <span style="color: #60efff;">Visibility: {current.get('visibility', 'N/A')} km</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_ml_features(features):
    """Display ML-extracted features with enhanced styling"""
    
    st.markdown("### 🔬 AI-Powered Roof Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #60efff; margin: 0;">Total Roof Area</h4>
            <p style="font-size: 2rem; color: #00ff87; font-family: 'Orbitron'; margin: 10px 0;">
                {features.get('roof_area_sqft', 0):,}
            </p>
            <p style="color: #888; margin: 0;">square feet</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #60efff; margin: 0;">Usable Area</h4>
            <p style="font-size: 2rem; color: #00ff87; font-family: 'Orbitron'; margin: 10px 0;">
                {features.get('usable_area_sqft', 0):,}
            </p>
            <p style="color: #888; margin: 0;">square feet</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #60efff; margin: 0;">Obstacles Detected</h4>
            <p style="font-size: 2rem; color: #ffd700; font-family: 'Orbitron'; margin: 10px 0;">
                {features.get('obstacle_count', 0)}
            </p>
            <p style="color: #888; margin: 0;">obstructions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        complexity = features.get('complexity_score', 0)
        color = "#00ff87" if complexity < 5 else "#ffd700" if complexity < 8 else "#ff6b6b"
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #60efff; margin: 0;">Complexity</h4>
            <p style="font-size: 2rem; color: {color}; font-family: 'Orbitron'; margin: 10px 0;">
                {complexity}/10
            </p>
            <p style="color: #888; margin: 0;">difficulty score</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Additional features
    st.markdown("#### 📊 Detailed Characteristics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**🧭 Orientation:** {features.get('orientation', 'Unknown')}")
    with col2:
        st.markdown(f"**📐 Roof Slope:** {features.get('roof_slope', 'Unknown')}")
    with col3:
        st.markdown(f"**🏗️ Material:** {features.get('roof_material', 'Unknown')}")
    with col4:
        shading = features.get('shading_percent', 0)
        st.markdown(f"**🌑 Shading:** {shading:.1f}%")


def create_score_gauge(score, title):
    """Create a gauge chart for suitability score"""
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 20, 'color': '#60efff'}},
        delta = {'reference': 7, 'increasing': {'color': "#00ff87"}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#60efff"},
            'bar': {'color': "#00ff87"},
            'bgcolor': "rgba(26, 31, 58, 0.5)",
            'borderwidth': 2,
            'bordercolor': "#60efff",
            'steps': [
                {'range': [0, 5], 'color': 'rgba(255, 107, 107, 0.3)'},
                {'range': [5, 7], 'color': 'rgba(255, 215, 0, 0.3)'},
                {'range': [7, 10], 'color': 'rgba(0, 255, 135, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "#ffd700", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#60efff", 'family': "Orbitron"},
        height=250
    )
    
    return fig


def display_technology_card(tech_name, tech_data, icon):
    """Display enhanced technology analysis card"""
    
    score = tech_data['suitability_score']
    
    # Score styling
    if score >= 8:
        score_class = "score-excellent"
        score_label = "EXCELLENT"
        badge_color = "#00ff87"
    elif score >= 6:
        score_class = "score-good"
        score_label = "GOOD"
        badge_color = "#ffd700"
    else:
        score_class = "score-fair"
        score_label = "FAIR"
        badge_color = "#ff6b6b"
    
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="color: {badge_color}; margin: 0;">{icon} {tech_name}</h2>
        <div style="display: flex; align-items: center; margin: 15px 0;">
            <p class='{score_class}' style="margin: 0; flex: 1;">{score}/10</p>
            <span style="background: {badge_color}; color: #0a0e27; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                {score_label}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gauge chart
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = create_score_gauge(score, "Suitability")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Technology-specific metrics
        if tech_name == "Solar Panels":
            st.markdown("#### 💰 Financial Metrics")
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("System Size", f"{tech_data['system_size_kw']:.1f} kW", 
                         delta=f"{tech_data['panel_count']} panels")
            with mcol2:
                st.metric("Annual Production", f"{tech_data['annual_production_kwh']:,} kWh",
                         delta=f"${tech_data['annual_savings_usd']:,}/yr")
            with mcol3:
                st.metric("Payback Period", f"{tech_data['payback_years']} years",
                         delta="ROI Timeline")
            
            st.markdown("#### 💵 Investment Analysis")
            cost_col1, cost_col2 = st.columns(2)
            with cost_col1:
                st.metric("Installation Cost", f"${tech_data['installation_cost_usd']:,}",
                         help="Total system cost after tax credits")
            with cost_col2:
                st.metric("Annual Savings", f"${tech_data['annual_savings_usd']:,}",
                         help="Estimated yearly electricity savings")
        
        elif tech_name == "Rainwater Harvesting":
            st.markdown("#### 💧 Water Collection Metrics")
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Annual Collection", f"{tech_data['annual_collection_liters']:,}L",
                         delta="Per year")
            with mcol2:
                st.metric("Tank Size Needed", f"{tech_data['tank_size_needed_liters']:,}L",
                         delta="Storage capacity")
            with mcol3:
                st.metric("Self-Sufficiency", f"{tech_data['water_self_sufficiency_percent']}%",
                         delta="Independence")
            
            st.markdown("#### 💵 Investment Analysis")
            cost_col1, cost_col2 = st.columns(2)
            with cost_col1:
                st.metric("Installation Cost", f"${tech_data['installation_cost_usd']:,}",
                         help="Includes tank, pipes, and filtration")
            with cost_col2:
                st.metric("Annual Savings", f"${tech_data['annual_savings_usd']:,}",
                         help="Estimated water bill savings")
        
        elif tech_name == "Rooftop Gardening":
            st.markdown("#### 🌱 Garden Potential")
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Plantable Area", f"{tech_data['plantable_area_sqft']} sqft",
                         delta="Available space")
            with mcol2:
                st.metric("Annual Yield", f"{tech_data['annual_yield_kg']} kg",
                         delta="Food production")
            with mcol3:
                st.metric("Annual Value", f"${tech_data['annual_value_usd']:,}",
                         delta="Market value")
            
            st.markdown("#### 🌿 Recommended Crops")
            crops_html = " ".join([f"<span style='background: rgba(0,255,135,0.2); padding: 5px 10px; border-radius: 15px; margin: 5px; display: inline-block; color: #00ff87;'>{crop}</span>" 
                                  for crop in tech_data['recommended_crops']])
            st.markdown(crops_html, unsafe_allow_html=True)
    
    # Expandable sections
    with st.expander("📝 Key Points", expanded=False):
        for point in tech_data['key_points']:
            st.markdown(f"• {point}")
    
    with st.expander("✅ Advantages", expanded=False):
        for pro in tech_data.get('pros', []):
            st.markdown(f"<p style='color: #00ff87;'>✓ {pro}</p>", unsafe_allow_html=True)
    
    with st.expander("⚠️ Considerations", expanded=False):
        for con in tech_data.get('cons', []):
            st.markdown(f"<p style='color: #ffd700;'>⚠ {con}</p>", unsafe_allow_html=True)
    
    if 'optimization_tips' in tech_data:
        with st.expander("💡 Optimization Tips", expanded=False):
            for tip in tech_data['optimization_tips']:
                st.markdown(f"<p style='color: #60efff;'>💡 {tip}</p>", unsafe_allow_html=True)
    
    if 'usage_recommendations' in tech_data:
        with st.expander("🎯 Usage Recommendations", expanded=False):
            for rec in tech_data['usage_recommendations']:
                st.markdown(f"<p style='color: #60efff;'>→ {rec}</p>", unsafe_allow_html=True)
    
    if 'seasonal_tips' in tech_data:
        with st.expander("📅 Seasonal Tips", expanded=False):
            for tip in tech_data['seasonal_tips']:
                st.markdown(f"<p style='color: #60efff;'>🌸 {tip}</p>", unsafe_allow_html=True)


def create_comparison_chart(results):
    """Create technology comparison chart"""
    
    comparison_df = pd.DataFrame({
        'Technology': ['Solar Panels', 'Rainwater Harvesting', 'Rooftop Gardening'],
        'Suitability Score': [
            results['solar']['suitability_score'],
            results['rainwater']['suitability_score'],
            results['gardening']['suitability_score']
        ],
        'Annual Savings': [
            results['solar']['annual_savings_usd'],
            results['rainwater']['annual_savings_usd'],
            results['gardening']['annual_value_usd']
        ]
    })
    
    # Suitability comparison
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=comparison_df['Technology'],
        y=comparison_df['Suitability Score'],
        marker=dict(
            color=comparison_df['Suitability Score'],
            colorscale=[[0, '#ff6b6b'], [0.5, '#ffd700'], [1, '#00ff87']],
            line=dict(color='#60efff', width=2)
        ),
        text=comparison_df['Suitability Score'],
        textposition='outside',
        textfont=dict(size=16, color='#00ff87', family='Orbitron')
    ))
    
    fig1.update_layout(
        title='Suitability Comparison',
        yaxis=dict(range=[0, 10], title='Score', gridcolor='rgba(96, 239, 255, 0.1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 31, 58, 0.5)',
        font=dict(color='#60efff', family='Rajdhani'),
        showlegend=False,
        height=400
    )
    
    # Financial comparison
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=comparison_df['Technology'],
        y=comparison_df['Annual Savings'],
        marker=dict(
            color=['#00ff87', '#60efff', '#ffd700'],
            line=dict(color='#60efff', width=2)
        ),
        text=['$' + str(int(x)) for x in comparison_df['Annual Savings']],
        textposition='outside',
        textfont=dict(size=14, color='#00ff87', family='Orbitron')
    ))
    
    fig2.update_layout(
        title='Annual Savings Comparison',
        yaxis=dict(title='USD/Year', gridcolor='rgba(96, 239, 255, 0.1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(26, 31, 58, 0.5)',
        font=dict(color='#60efff', family='Rajdhani'),
        showlegend=False,
        height=400
    )
    
    return fig1, fig2


# END OF PART 2
# Continue with Part 3 for main() function
# app.py - PART 3 (FINAL)
# Copy this after Part 2 to complete your app.py file

def create_environmental_impact_chart(impact_data):
    """Create environmental impact visualization"""
    
    categories = ['CO₂ Offset', 'Water Saved', 'Food Produced']
    values = [
        impact_data['co2_offset_tons_per_year'],
        impact_data['water_saved_liters_per_year'] / 1000,  # Convert to thousands
        impact_data['food_produced_kg_per_year']
    ]
    units = ['tons/year', 'K liters/year', 'kg/year']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 255, 135, 0.3)',
        line=dict(color='#00ff87', width=3),
        marker=dict(size=10, color='#60efff')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='rgba(96, 239, 255, 0.2)',
                tickfont=dict(color='#60efff')
            ),
            angularaxis=dict(
                gridcolor='rgba(96, 239, 255, 0.2)',
                tickfont=dict(size=14, color='#00ff87', family='Rajdhani')
            ),
            bgcolor='rgba(26, 31, 58, 0.5)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#60efff'),
        showlegend=False,
        height=400
    )
    
    return fig


def main():
    initialize_session_state()
    
    # Header with animated title
    st.markdown('<h1 class="main-title">🌱 GREEN ROOFTOP ANALYZER</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-POWERED MULTI-TECHNOLOGY SUSTAINABILITY ASSESSMENT</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📍 LOCATION SETTINGS")
        
        address_input = st.text_input(
            "Enter Address or Coordinates",
            placeholder="e.g., 'New York, USA' or '28.6139, 77.2090'",
            help="Enter city name, full address, or coordinates (lat, lon)"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 LOCATE", use_container_width=True):
                if address_input:
                    with st.spinner("Locating..."):
                        location_api = LocationAPI()
                        location_data = location_api.address_to_coords(address_input)
                        st.session_state.location_data = location_data
                        
                        # Fetch weather for new location
                        weather_api = WeatherAPI()
                        weather_data = weather_api.get_weather_data(
                            location_data['lat'], 
                            location_data['lon']
                        )
                        st.session_state.weather_data = weather_data
                        st.success(f"✓ Located!")
                        st.rerun()
                else:
                    st.warning("Please enter a location")
        
        with col2:
            if st.button("🎯 USE GPS", use_container_width=True):
                st.info("GPS feature requires location permission")
        
        # Initialize default location if none set
        if st.session_state.location_data is None:
            location_api = LocationAPI()
            st.session_state.location_data = location_api.address_to_coords("New Delhi, India")
            weather_api = WeatherAPI()
            st.session_state.weather_data = weather_api.get_weather_data(
                st.session_state.location_data['lat'],
                st.session_state.location_data['lon']
            )
        
        # Display current location
        if st.session_state.location_data:
            loc = st.session_state.location_data
            st.markdown(f"""
            <div class="info-box">
                <strong>📌 Current Location</strong><br>
                {loc.get('address', 'Location not resolved')}<br>
                <small>Lat: {loc['lat']:.4f}, Lon: {loc['lon']:.4f}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Weather widget in sidebar
        if st.session_state.weather_data:
            create_weather_widget(st.session_state.weather_data)
        
        st.markdown("---")
        
        # Tech stack info
        st.markdown("""
        <div class="info-box">
            <strong>🤖 TECH STACK</strong><br>
            • ML: SAM + ResNet + CV<br>
            • AI: Google Gemini<br>
            • Weather: OpenWeather<br>
            • Maps: Nominatim OSM
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("v1.0 | Built with Streamlit")
    
    # Main content area
    st.markdown("### 📸 UPLOAD ROOFTOP IMAGE")
    
    uploaded_file = st.file_uploader(
        "Choose an aerial/satellite image of the rooftop",
        type=['jpg', 'jpeg', 'png'],
        help="Best results with clear, overhead view"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="📷 Uploaded Rooftop Image", use_container_width=True)
        
        with col2:
            st.markdown("### 🚀 READY TO ANALYZE")
            
            if st.session_state.location_data:
                loc = st.session_state.location_data
            st.markdown(f"""
                <div class="metric-card">
                    <p><strong>Location:</strong><br>{get_city_name(loc)}, {loc.get('country', 'Unknown Country')}</p>
                    <p><strong>Image Size:</strong> {image.size[0]} x {image.size[1]} px</p>
                    <p><strong>Climate:</strong> {st.session_state.weather_data['current']['description'] if st.session_state.weather_data else 'Loading...'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("🚀 ANALYZE ROOFTOP", type="primary", use_container_width=True):
                success = analyze_rooftop(image, st.session_state.location_data)
                if success:
                    st.success("✅ Analysis Complete!")
                    st.rerun()
        
        # Display results if analysis complete
        if st.session_state.analysis_complete:
            st.markdown("---")
            
            # ML Features Section
            st.markdown("## 🔬 MACHINE LEARNING ANALYSIS")
            display_ml_features(st.session_state.ml_features)
            
            st.markdown("---")
            
            # Technology Analysis Tabs
            st.markdown("## 🌿 GREEN TECHNOLOGY ASSESSMENT")
            
            results = st.session_state.gemini_results
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "☀️ SOLAR PANELS",
                "💧 RAINWATER HARVESTING",
                "🌱 ROOFTOP GARDENING",
                "📊 OVERALL SUMMARY"
            ])
            
            with tab1:
                st.markdown("### ☀️ Solar Panel Analysis")
                display_technology_card("Solar Panels", results['solar'], "☀️")
                
                # Additional solar-specific visualizations
                st.markdown("#### 📈 Production & Savings Projection")
                years = list(range(1, 26))
                degradation = 0.005
                annual_prod = results['solar']['annual_production_kwh']
                production = [annual_prod * ((1 - degradation) ** year) for year in years]
                savings = [prod * 0.13 for prod in production]  # $0.13/kWh
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=years, y=production,
                    name='Production (kWh)',
                    line=dict(color='#00ff87', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(0, 255, 135, 0.2)'
                ))
                
                fig.update_layout(
                    title='25-Year Energy Production Forecast',
                    xaxis_title='Year',
                    yaxis_title='kWh',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 31, 58, 0.5)',
                    font=dict(color='#60efff', family='Rajdhani'),
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown("### 💧 Rainwater Harvesting Analysis")
                display_technology_card("Rainwater Harvesting", results['rainwater'], "💧")
                
                # Monthly collection estimate
                st.markdown("#### 📊 Estimated Monthly Collection")
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                # Simulate seasonal variation
                annual = results['rainwater']['annual_collection_liters']
                monthly = [annual/12 * (0.5 + np.random.random()) for _ in months]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=months,
                    y=monthly,
                    marker=dict(
                        color=monthly,
                        colorscale='Blues',
                        line=dict(color='#60efff', width=2)
                    ),
                    text=[f'{int(v)}L' for v in monthly],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Monthly Water Collection Pattern',
                    yaxis_title='Liters',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 31, 58, 0.5)',
                    font=dict(color='#60efff', family='Rajdhani'),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.markdown("### 🌱 Rooftop Gardening Analysis")
                display_technology_card("Rooftop Gardening", results['gardening'], "🌱")
                
                # Crop yield breakdown
                st.markdown("#### 🥬 Crop Yield Distribution")
                crops = results['gardening']['recommended_crops']
                total_yield = results['gardening']['annual_yield_kg']
                yields = [total_yield / len(crops) * (0.8 + np.random.random() * 0.4) for _ in crops]
                
                fig = go.Figure(data=[go.Pie(
                    labels=crops,
                    values=yields,
                    hole=0.4,
                    marker=dict(
                        colors=['#00ff87', '#60efff', '#ffd700', '#ff6b6b', '#a78bfa'],
                        line=dict(color='#0a0e27', width=2)
                    ),
                    textfont=dict(size=14, color='white', family='Rajdhani')
                )])
                
                fig.update_layout(
                    title='Expected Crop Distribution',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#60efff', family='Rajdhani'),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.markdown("### 🏆 OVERALL RECOMMENDATION")
                
                overall = results['overall']
                
                # Best technology highlight
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(0, 255, 135, 0.2), rgba(96, 239, 255, 0.2));">
                    <h2 style="color: #00ff87;">Recommended: {overall['best_technology'].upper()}</h2>
                    <p style="font-size: 1.2rem; color: #60efff;">{overall['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Implementation priority
                st.markdown("#### 🎯 Implementation Priority")
                for i, tech in enumerate(overall['implementation_priority'], 1):
                    color = "#00ff87" if i == 1 else "#ffd700" if i == 2 else "#60efff"
                    st.markdown(f"<p style='color: {color}; font-size: 1.2rem;'>{i}. {tech}</p>", 
                               unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Financial overview
                st.markdown("#### 💰 Financial Overview")
                fin_col1, fin_col2, fin_col3 = st.columns(3)
                
                with fin_col1:
                    st.metric(
                        "Total Investment",
                        f"${overall['total_investment_usd']:,}",
                        help="Combined cost of all technologies"
                    )
                
                with fin_col2:
                    st.metric(
                        "Annual Savings",
                        f"${overall['total_annual_savings_usd']:,}",
                        help="Combined yearly savings"
                    )
                
                with fin_col3:
                    combined_payback = overall['total_investment_usd'] / overall['total_annual_savings_usd'] if overall['total_annual_savings_usd'] > 0 else 99
                    st.metric(
                        "Combined Payback",
                        f"{combined_payback:.1f} years",
                        help="Time to recover investment"
                    )
                
                st.markdown("---")
                
                # Environmental Impact
                st.markdown("#### 🌍 Environmental Impact")
                
                impact = overall['environmental_impact']
                
                impact_col1, impact_col2, impact_col3 = st.columns(3)
                
                with impact_col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #00ff87;">🌳 CO₂ Offset</h4>
                        <p style="font-size: 2rem; color: #00ff87; font-family: 'Orbitron';">
                            {impact['co2_offset_tons_per_year']:.1f}
                        </p>
                        <p style="color: #888;">tons/year</p>
                        <small style="color: #60efff;">≈ {int(impact['co2_offset_tons_per_year'] * 16)} trees planted</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with impact_col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #60efff;">💧 Water Saved</h4>
                        <p style="font-size: 2rem; color: #60efff; font-family: 'Orbitron';">
                            {impact['water_saved_liters_per_year']:,}
                        </p>
                        <p style="color: #888;">liters/year</p>
                        <small style="color: #60efff;">≈ {impact['water_saved_liters_per_year']} bottles</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with impact_col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4 style="color: #ffd700;">🥬 Food Produced</h4>
                        <p style="font-size: 2rem; color: #ffd700; font-family: 'Orbitron';">
                            {impact['food_produced_kg_per_year']}
                        </p>
                        <p style="color: #888;">kg/year</p>
                        <small style="color: #60efff;">≈ {impact['food_produced_kg_per_year'] * 3} meals</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Environmental impact radar chart
                st.markdown("#### 📊 Impact Visualization")
                impact_fig = create_environmental_impact_chart(impact)
                st.plotly_chart(impact_fig, use_container_width=True)
                
                st.markdown("---")
                
                # Comparison charts
                st.markdown("#### 📈 Technology Comparison")
                fig1, fig2 = create_comparison_chart(results)
                
                comp_col1, comp_col2 = st.columns(2)
                with comp_col1:
                    st.plotly_chart(fig1, use_container_width=True)
                with comp_col2:
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Download report section
            st.markdown("---")
            st.markdown("### 📄 EXPORT REPORT")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                report_data = {
                    'location': st.session_state.location_data,
                    'ml_features': st.session_state.ml_features,
                    'weather_data': st.session_state.weather_data,
                    'analysis_results': st.session_state.gemini_results,
                    'timestamp': datetime.now().isoformat()
                }
                
                json_str = json.dumps(report_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"rooftop_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # CSV export
                csv_data = pd.DataFrame([{
                    'Technology': 'Solar',
                    'Score': results['solar']['suitability_score'],
                    'Investment': results['solar']['installation_cost_usd'],
                    'Annual_Savings': results['solar']['annual_savings_usd']
                }, {
                    'Technology': 'Rainwater',
                    'Score': results['rainwater']['suitability_score'],
                    'Investment': results['rainwater']['installation_cost_usd'],
                    'Annual_Savings': results['rainwater']['annual_savings_usd']
                }, {
                    'Technology': 'Gardening',
                    'Score': results['gardening']['suitability_score'],
                    'Investment': results['gardening']['setup_cost_usd'],
                    'Annual_Savings': results['gardening']['annual_value_usd']
                }])
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data.to_csv(index=False),
                    file_name=f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                st.button("🖨️ Print Report", use_container_width=True, help="Use browser print (Ctrl+P)")
    
    else:
        # Instructions when no image uploaded
        st.markdown("""
        <div class="info-box">
            <h3>📋 How to Use</h3>
            <ol>
                <li><strong>Set Location:</strong> Enter your address or coordinates in the sidebar</li>
                <li><strong>Upload Image:</strong> Choose an aerial/satellite image of the rooftop</li>
                <li><strong>Analyze:</strong> Click the analyze button to start AI assessment</li>
                <li><strong>Review Results:</strong> Explore detailed analysis for each technology</li>
                <li><strong>Export:</strong> Download comprehensive reports in JSON/CSV format</li>
            </ol>
            
            <h3>💡 Tips for Best Results</h3>
            <ul>
                <li>Use clear, overhead images (satellite or drone)</li>
                <li>Ensure entire roof is visible</li>
                <li>Higher resolution = better accuracy</li>
                <li>Avoid images with heavy shadows or obstructions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #60efff; padding: 30px;'>
        <p style='font-size: 1.2rem; font-family: "Orbitron";'><strong>GREEN ROOFTOP ANALYZER v1.0</strong></p>
        <p style='color: #888;'>🤖 Powered by SAM + ResNet + Google Gemini | 🌐 Built with Streamlit</p>
        <p style='color: #888;'>🎓 Academic Major Project | 🌱 Building a Sustainable Future</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
