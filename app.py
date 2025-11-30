# app.py
# AAVA - Authorised Address Validation Agency
# Main Streamlit Application
# 
# This is the entry point for the AAVA web application.
# Run with: streamlit run app.py

"""
AAVA Dashboard
==============
A multi-page Streamlit application for address validation in India's
DHRUVA Digital Address Ecosystem.

Features:
- Dashboard with metrics and analytics
- DIGIPIN encoder/decoder
- Confidence score calculator
- Address validation management
- Agent portal for field verification
- Admin panel for system management
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import json
import base64
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_database, DatabaseManager
from PIL import Image

# =============================================================================
# DEVELOPER & VISITOR CONFIG
# =============================================================================

VISITOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "visitors.json")
PROFILE_PIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "profile.png")

DEVELOPER = {
    "name": "Raj Kumar",
    "email": "rajkumar648321@gmail.com",
    "phone": "7061001946",
    "linkedin": "https://www.linkedin.com/in/raj-kumar-9a149a280",
    "github": "https://github.com/Razz0711",
    "role": "Data Science & ML Enthusiast | Stock Market Enthusiast"
}

def increment_visitor():
    """Track unique visitors."""
    try:
        data_dir = os.path.dirname(VISITOR_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        total, sessions = 0, []
        if os.path.exists(VISITOR_FILE):
            with open(VISITOR_FILE, 'r') as f:
                data = json.load(f)
                total, sessions = data.get("total_visits", 0), data.get("sessions", [])
        
        session_id = str(id(st.session_state))
        if session_id not in sessions:
            total += 1
            sessions = (sessions + [session_id])[-1000:]
            with open(VISITOR_FILE, 'w') as f:
                json.dump({"total_visits": total, "sessions": sessions}, f)
        
        return total
    except:
        return 0
from utils.digipin import DIGIPINValidator, encode_digipin, decode_digipin
from utils.confidence_score import (
    ConfidenceScoreCalculator, 
    SampleDataGenerator,
    get_grade_color
)
from utils.premium_theme import PREMIUM_CSS, PAGE_GRADIENTS


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="AAVA - Address Validation Agency",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/aava-system',
        'Report a bug': 'https://github.com/aava-system/issues',
        'About': """
        # AAVA - Authorised Address Validation Agency
        
        Part of India's DHRUVA Digital Address Ecosystem.
        """
    }
)


# =============================================================================
# APPLY PREMIUM THEME
# =============================================================================

st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# Additional App-specific CSS
st.markdown("""
<style>
    /* Grade badges */
    .grade-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.5rem;
        color: white;
        text-align: center;
        min-width: 60px;
    }
    
    .grade-a-plus { background: #00C853; }
    .grade-a { background: #00E676; }
    .grade-b { background: #FFEB3B; color: #333; }
    .grade-c { background: #FFC107; color: #333; }
    .grade-d { background: #FF9800; }
    .grade-f { background: #F44336; }
    
    /* DIGIPIN display */
    .digipin-display {
        font-family: 'Courier New', monospace;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #00d4ff 0%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
        text-align: center;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-pending { background: rgba(255,171,0,0.2); color: #ffab00; }
    .status-progress { background: rgba(33,150,243,0.2); color: #2196F3; }
    .status-completed { background: rgba(0,230,118,0.2); color: #00e676; }
    .status-failed { background: rgba(255,82,82,0.2); color: #ff5252; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'db' not in st.session_state:
        st.session_state.db = get_database()
    
    if 'digipin_validator' not in st.session_state:
        st.session_state.digipin_validator = DIGIPINValidator()
    
    if 'confidence_calculator' not in st.session_state:
        st.session_state.confidence_calculator = ConfidenceScoreCalculator()
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = None

init_session_state()


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():
    """Render the sidebar with navigation and info."""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #1e3a5f; margin: 0;">🏠 AAVA</h1>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                Address Validation Agency
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        
        try:
            stats = st.session_state.db.get_dashboard_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Addresses", stats.get('total_addresses', 0))
                st.metric("Agents", stats.get('active_agents', 0))
            with col2:
                st.metric("Validations", stats.get('total_validations', 0))
                st.metric("Today", stats.get('validations_today', 0))
        except Exception as e:
            st.info("Loading stats...")
        
        st.divider()
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.markdown(f"""
        - **Version:** 1.0.0
        - **Date:** {datetime.now().strftime('%Y-%m-%d')}
        - **Status:** 🟢 Online
        """)
        
        st.divider()
        
        # About section
        with st.expander("About AAVA"):
            st.markdown("""
            **AAVA** (Authorised Address Validation Agency) is part of 
            India's DHRUVA Digital Address Ecosystem.
            
            **Key Features:**
            - 📍 DIGIPIN validation
            - 📊 Confidence scoring
            - ✅ Physical verification
            - 🔒 Privacy-first design
            """)

render_sidebar()


# =============================================================================
# MAIN HEADER
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1>🏠 AAVA Dashboard</h1>
    <p>Authorised Address Validation Agency • DHRUVA Digital Address Ecosystem</p>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MAIN TABS
# =============================================================================

tab1, tab2, tab3 = st.tabs([
    "📊 Dashboard",
    "📍 DIGIPIN Tester",
    "📈 Confidence Score Tester"
])


# -----------------------------------------------------------------------------
# TAB 1: DASHBOARD
# -----------------------------------------------------------------------------

with tab1:
    st.markdown("### System Overview")
    
    # Metrics row
    try:
        stats = st.session_state.db.get_dashboard_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Addresses",
                value=f"{stats.get('total_addresses', 0):,}",
                delta="+12 today" if stats.get('total_addresses', 0) > 0 else None
            )
        
        with col2:
            st.metric(
                label="Total Validations",
                value=f"{stats.get('total_validations', 0):,}",
                delta=f"+{stats.get('validations_today', 0)} today"
            )
        
        with col3:
            st.metric(
                label="Pending",
                value=f"{stats.get('pending_validations', 0):,}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Completed",
                value=f"{stats.get('completed_validations', 0):,}",
                delta=None
            )
        
        with col5:
            avg_conf = stats.get('avg_confidence', 0)
            st.metric(
                label="Avg Confidence",
                value=f"{avg_conf:.1f}%" if avg_conf else "N/A",
                delta=None
            )
    
    except Exception as e:
        st.info("📊 Dashboard metrics will appear once data is available.")
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Validation Status Distribution")
        
        # Create sample data for demonstration
        try:
            val_stats = st.session_state.db.get_validation_stats()
            status_data = val_stats.get('by_status', {})
            
            if status_data:
                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9E9E9E'],
                    hole=0.4
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Show demo chart
                demo_data = {
                    'COMPLETED': 45,
                    'PENDING': 25,
                    'IN_PROGRESS': 20,
                    'FAILED': 10
                }
                fig = px.pie(
                    values=list(demo_data.values()),
                    names=list(demo_data.keys()),
                    color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3', '#F44336'],
                    hole=0.4
                )
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2)
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("📊 Demo data - Add validations to see real statistics")
        except:
            st.info("No validation data available yet.")
    
    with col2:
        st.markdown("#### Confidence Score Distribution")
        
        # Generate sample distribution
        import numpy as np
        np.random.seed(42)
        
        # Sample scores with realistic distribution
        scores = np.concatenate([
            np.random.normal(85, 8, 30),   # High scorers
            np.random.normal(70, 10, 40),  # Medium scorers
            np.random.normal(50, 12, 20),  # Low scorers
            np.random.normal(35, 8, 10)    # Very low
        ])
        scores = np.clip(scores, 0, 100)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            marker_color='#2d5a87',
            opacity=0.8
        ))
        
        # Add grade zones
        fig.add_vrect(x0=90, x1=100, fillcolor="green", opacity=0.1, annotation_text="A+")
        fig.add_vrect(x0=80, x1=90, fillcolor="lightgreen", opacity=0.1, annotation_text="A")
        fig.add_vrect(x0=70, x1=80, fillcolor="yellow", opacity=0.1, annotation_text="B")
        fig.add_vrect(x0=60, x1=70, fillcolor="orange", opacity=0.1, annotation_text="C")
        fig.add_vrect(x0=50, x1=60, fillcolor="darkorange", opacity=0.1, annotation_text="D")
        fig.add_vrect(x0=0, x1=50, fillcolor="red", opacity=0.1, annotation_text="F")
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
            xaxis_title="Confidence Score",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📊 Sample distribution - Real data will appear as addresses are scored")
    
    st.divider()
    
    # Recent activity
    st.markdown("#### Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📋 Recent Validations")
        try:
            recent_validations = st.session_state.db.get_all_validations(limit=5)
            if recent_validations:
                for val in recent_validations:
                    status_class = {
                        'PENDING': 'status-pending',
                        'IN_PROGRESS': 'status-progress',
                        'COMPLETED': 'status-completed',
                        'FAILED': 'status-failed'
                    }.get(val.get('status', 'PENDING'), 'status-pending')
                    
                    st.markdown(f"""
                    <div class="card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{val.get('id', 'N/A')}</strong><br>
                                <span style="color: #666; font-size: 0.85rem;">
                                    {val.get('digital_address', val.get('digipin', 'No address'))}
                                </span>
                            </div>
                            <span class="status-badge {status_class}">{val.get('status', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No validations yet. Create one from the Validation Request page!")
        except Exception as e:
            st.info("No recent validations to display.")
    
    with col2:
        st.markdown("##### 👥 Active Agents")
        try:
            agents = st.session_state.db.get_all_agents(active_only=True)
            if agents:
                for agent in agents[:5]:
                    perf_score = agent.get('performance_score', 0) * 100
                    color = '#4CAF50' if perf_score >= 80 else '#FF9800' if perf_score >= 60 else '#F44336'
                    
                    st.markdown(f"""
                    <div class="card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{agent.get('name', 'Unknown')}</strong><br>
                                <span style="color: #666; font-size: 0.85rem;">
                                    {agent.get('id', '')}
                                </span>
                            </div>
                            <span style="color: {color}; font-weight: 600;">
                                {perf_score:.0f}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No agents registered yet. Add agents from the Admin Panel!")
        except Exception as e:
            st.info("No agents to display.")


# -----------------------------------------------------------------------------
# TAB 2: DIGIPIN TESTER
# -----------------------------------------------------------------------------

with tab2:
    st.markdown("### 📍 DIGIPIN Encoder/Decoder")
    st.markdown("""
    DIGIPIN is a 10-character geo-coded grid system that uniquely identifies 
    a ~4m × 4m area anywhere in India. Test the encoding and decoding below.
    """)
    
    validator = st.session_state.digipin_validator
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌍 Coordinates → DIGIPIN")
        st.markdown("Enter coordinates to generate a DIGIPIN code.")
        
        # Preset locations
        presets = {
            "Custom": (0, 0),
            "New Delhi (India Gate)": (28.6129, 77.2295),
            "Mumbai (Gateway of India)": (18.9220, 72.8347),
            "Bangalore (Vidhana Soudha)": (12.9716, 77.5946),
            "Chennai (Marina Beach)": (13.0500, 80.2824),
            "Kolkata (Victoria Memorial)": (22.5448, 88.3426),
            "Hyderabad (Charminar)": (17.3616, 78.4747),
        }
        
        selected_preset = st.selectbox(
            "Choose a location or enter custom coordinates:",
            options=list(presets.keys()),
            key="encode_preset"
        )
        
        if selected_preset == "Custom":
            lat = st.number_input(
                "Latitude (2.5° to 38.5°)",
                min_value=2.5,
                max_value=38.5,
                value=28.6129,
                step=0.0001,
                format="%.6f",
                key="encode_lat"
            )
            lon = st.number_input(
                "Longitude (63.5° to 99.5°)",
                min_value=63.5,
                max_value=99.5,
                value=77.2295,
                step=0.0001,
                format="%.6f",
                key="encode_lon"
            )
        else:
            lat, lon = presets[selected_preset]
            st.info(f"📍 Using coordinates: ({lat}, {lon})")
        
        if st.button("🔄 Encode to DIGIPIN", type="primary", key="encode_btn"):
            result = validator.encode(lat, lon)
            
            if result.valid:
                st.success("✅ DIGIPIN Generated Successfully!")
                
                st.markdown(f"""
                <div style="text-align: center; margin: 1.5rem 0;">
                    <div class="digipin-display">{result.formatted}</div>
                    <p style="color: #666; margin-top: 0.5rem;">
                        Resolution: {result.resolution_meters:.2f} meters
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📋 Details"):
                    st.json({
                        'digipin': result.digipin,
                        'formatted': result.formatted,
                        'center_lat': round(result.center_lat, 8),
                        'center_lon': round(result.center_lon, 8),
                        'bounds': {k: round(v, 8) for k, v in result.bounds.items()},
                        'resolution_meters': round(result.resolution_meters, 4)
                    })
            else:
                st.error(f"❌ Error: {result.error}")
    
    with col2:
        st.markdown("#### 🔍 DIGIPIN → Coordinates")
        st.markdown("Enter a DIGIPIN code to decode its location.")
        
        digipin_input = st.text_input(
            "Enter DIGIPIN (e.g., 3PJ-K4M-5L2T):",
            placeholder="XXX-XXX-XXXX",
            key="decode_input"
        ).upper()
        
        # Validate format on input
        if digipin_input:
            is_valid, message = validator.validate_with_details(digipin_input)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.warning(f"⚠️ {message}")
        
        if st.button("🔄 Decode DIGIPIN", type="primary", key="decode_btn"):
            if digipin_input:
                result = validator.decode(digipin_input)
                
                if result.valid:
                    st.success("✅ DIGIPIN Decoded Successfully!")
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin: 1.5rem 0;">
                        <h3 style="margin: 0;">📍 Location</h3>
                        <p style="font-size: 1.2rem; margin: 0.5rem 0;">
                            <strong>Lat:</strong> {result.center_lat:.6f}°N<br>
                            <strong>Lon:</strong> {result.center_lon:.6f}°E
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a simple map visualization using Plotly
                    fig = go.Figure(go.Scattermapbox(
                        lat=[result.center_lat],
                        lon=[result.center_lon],
                        mode='markers',
                        marker=go.scattermapbox.Marker(size=14, color='red'),
                        text=[result.formatted],
                        hoverinfo='text'
                    ))
                    
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            center=dict(lat=result.center_lat, lon=result.center_lon),
                            zoom=15
                        ),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("📋 Full Details"):
                        st.json({
                            'digipin': result.digipin,
                            'formatted': result.formatted,
                            'center_lat': round(result.center_lat, 8),
                            'center_lon': round(result.center_lon, 8),
                            'bounds': {k: round(v, 8) for k, v in result.bounds.items()},
                            'resolution_meters': round(result.resolution_meters, 4)
                        })
                else:
                    st.error(f"❌ Error: {result.error}")
            else:
                st.warning("Please enter a DIGIPIN code")
    
    st.divider()
    
    # Distance calculator
    st.markdown("#### 📏 Distance Calculator")
    st.markdown("Calculate the distance between two DIGIPINs.")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        digipin1 = st.text_input(
            "First DIGIPIN:",
            placeholder="XXX-XXX-XXXX",
            key="dist_digipin1"
        ).upper()
    
    with col2:
        digipin2 = st.text_input(
            "Second DIGIPIN:",
            placeholder="XXX-XXX-XXXX",
            key="dist_digipin2"
        ).upper()
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        calc_btn = st.button("Calculate", type="primary", key="calc_dist_btn")
    
    if calc_btn and digipin1 and digipin2:
        distance = validator.distance_between(digipin1, digipin2)
        
        if distance is not None:
            if distance < 1000:
                dist_str = f"{distance:.2f} meters"
            else:
                dist_str = f"{distance/1000:.2f} kilometers"
            
            st.success(f"📏 Distance: **{dist_str}**")
        else:
            st.error("❌ Invalid DIGIPIN(s). Please check the format.")


# -----------------------------------------------------------------------------
# TAB 3: CONFIDENCE SCORE TESTER
# -----------------------------------------------------------------------------

with tab3:
    st.markdown("### 📈 Confidence Score Calculator")
    st.markdown("""
    Test the confidence score algorithm with sample data or custom parameters.
    The score (0-100) is calculated based on 4 components.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📊 Component Weights")
        st.markdown("Adjust the weights for each scoring component:")
        
        w1 = st.slider(
            "Delivery Success Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.30,
            step=0.05,
            key="weight_dsr"
        )
        
        w2 = st.slider(
            "Spatial Consistency",
            min_value=0.0,
            max_value=1.0,
            value=0.30,
            step=0.05,
            key="weight_sc"
        )
        
        w3 = st.slider(
            "Temporal Freshness",
            min_value=0.0,
            max_value=1.0,
            value=0.20,
            step=0.05,
            key="weight_tf"
        )
        
        w4 = st.slider(
            "Physical Verification",
            min_value=0.0,
            max_value=1.0,
            value=0.20,
            step=0.05,
            key="weight_pvs"
        )
        
        # Check if weights sum to 1
        total_weight = w1 + w2 + w3 + w4
        if abs(total_weight - 1.0) > 0.01:
            st.warning(f"⚠️ Weights sum to {total_weight:.2f} (should be 1.0)")
        else:
            st.success("✅ Weights are valid")
    
    with col2:
        st.markdown("#### 🎲 Sample Data Parameters")
        
        num_deliveries = st.slider(
            "Number of deliveries",
            min_value=1,
            max_value=50,
            value=15,
            key="sample_deliveries"
        )
        
        success_rate = st.slider(
            "Delivery success rate",
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.05,
            key="sample_success"
        )
        
        num_verifications = st.slider(
            "Number of physical verifications",
            min_value=0,
            max_value=5,
            value=1,
            key="sample_verifications"
        )
        
        days_old = st.slider(
            "Days since creation",
            min_value=1,
            max_value=365,
            value=60,
            key="sample_days"
        )
    
    if st.button("🔄 Calculate Sample Score", type="primary", key="calc_score_btn"):
        # Generate sample address
        address = SampleDataGenerator.generate_address(
            num_deliveries=num_deliveries,
            num_verifications=num_verifications,
            success_rate=success_rate
        )
        
        # Create calculator with custom weights
        try:
            calculator = ConfidenceScoreCalculator(
                weights={
                    'delivery_success': w1,
                    'spatial_consistency': w2,
                    'temporal_freshness': w3,
                    'physical_verification': w4
                }
            )
            
            result = calculator.calculate(address)
            
            st.divider()
            
            # Display results
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=result.score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confidence Score", 'font': {'size': 24}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': get_grade_color(result.grade)},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(244,67,54,0.2)"},
                            {'range': [50, 60], 'color': "rgba(255,152,0,0.2)"},
                            {'range': [60, 70], 'color': "rgba(255,193,7,0.2)"},
                            {'range': [70, 80], 'color': "rgba(255,235,59,0.2)"},
                            {'range': [80, 90], 'color': "rgba(0,230,118,0.2)"},
                            {'range': [90, 100], 'color': "rgba(0,200,83,0.2)"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': result.score
                        }
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                # Grade badge
                grade_class = f"grade-{result.grade.lower().replace('+', '-plus')}"
                st.markdown(f"""
                <div style="text-align: center;">
                    <span class="grade-badge {grade_class}">{result.grade}</span>
                    <p style="margin-top: 0.5rem; color: #666;">{result.grade_description}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Component breakdown
            st.markdown("#### 📊 Component Breakdown")
            
            components_data = []
            for key, comp in result.components.items():
                components_data.append({
                    'Component': comp.name,
                    'Raw Score': f"{comp.raw_value:.2%}",
                    'Weight': f"{comp.weight:.0%}",
                    'Weighted': f"{comp.weighted_value:.4f}",
                    'Data Points': comp.data_points
                })
            
            df = pd.DataFrame(components_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Visualization
            fig = go.Figure()
            
            colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
            
            for i, (key, comp) in enumerate(result.components.items()):
                fig.add_trace(go.Bar(
                    name=comp.name,
                    x=[comp.name],
                    y=[comp.raw_value * 100],
                    marker_color=colors[i],
                    text=[f"{comp.raw_value:.0%}"],
                    textposition='outside'
                ))
            
            fig.update_layout(
                title="Component Scores",
                yaxis_title="Score (%)",
                yaxis_range=[0, 110],
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            if result.recommendations:
                st.markdown("#### 💡 Recommendations")
                for rec in result.recommendations:
                    st.markdown(f"- {rec}")
        
        except ValueError as e:
            st.error(f"❌ Error: {str(e)}")


# =============================================================================
# DEVELOPER SECTION - Professional Design
# =============================================================================

st.markdown("---")

visitor_count = increment_visitor()

# Load and encode profile image
img_base64 = ""
if os.path.exists(PROFILE_PIC):
    try:
        with open(PROFILE_PIC, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
    except:
        pass

# CSS Styles - separate markdown call
st.markdown("""
<style>
.developer-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 16px;
    padding: 25px;
    color: white;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    border-top: 3px solid #667eea;
    margin: 15px 0;
}
.dev-flex {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 30px;
}
.dev-profile {
    display: flex;
    align-items: center;
    gap: 25px;
}
.dev-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 3px solid #667eea;
    object-fit: cover;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}
.dev-name {
    margin: 0 0 3px 0;
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}
.dev-role {
    margin: 0;
    opacity: 0.8;
    font-size: 0.95rem;
    color: #ddd;
}
.dev-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 8px 20px;
    border-radius: 25px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 10px;
}
.stat-box {
    text-align: center;
    padding: 12px 20px;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #667eea;
}
.stat-label {
    font-size: 0.85rem;
    opacity: 0.8;
    margin-top: 5px;
    color: #ddd;
}
.dev-footer {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid rgba(255,255,255,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.dev-links {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}
.dev-link {
    padding: 6px 16px;
    background: rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    color: white !important;
    text-decoration: none;
    font-size: 0.85rem;
    border: 1px solid rgba(102, 126, 234, 0.5);
}
.dev-link:hover {
    background: rgba(102, 126, 234, 0.6);
}
</style>
""", unsafe_allow_html=True)

# HTML Content - separate markdown call
if img_base64:
    avatar_html = f'<img src="data:image/png;base64,{img_base64}" class="dev-avatar">'
else:
    avatar_html = '<div class="dev-avatar" style="background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:2.5rem;">👨‍💻</div>'

st.markdown(f"""
<div class="developer-card">
    <div class="dev-flex">
        <div class="dev-profile">
            {avatar_html}
            <div>
                <h3 class="dev-name">{DEVELOPER['name']}</h3>
                <p class="dev-role">{DEVELOPER['role']}</p>
            </div>
        </div>
    </div>
    <div class="dev-footer">
        <div class="dev-links">
            <a href="mailto:{DEVELOPER['email']}" class="dev-link">📧 {DEVELOPER['email']}</a>
            <a href="tel:{DEVELOPER['phone']}" class="dev-link">📱 {DEVELOPER['phone']}</a>
        </div>
        <div class="dev-links">
            <a href="{DEVELOPER['linkedin']}" target="_blank" class="dev-link">🔗 LinkedIn</a>
            <a href="{DEVELOPER['github']}" target="_blank" class="dev-link">💻 GitHub</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown(f"""
<div class="footer">
    <p>
        <strong>AAVA</strong> - Authorised Address Validation Agency<br>
        Part of India's DHRUVA Digital Address Ecosystem
    </p>
</div>
""", unsafe_allow_html=True)
