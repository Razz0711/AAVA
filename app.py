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
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_database, DatabaseManager
from PIL import Image

# =============================================================================
# DEVELOPER & VISITOR CONFIG
# =============================================================================

VISITOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "visitors.json")
PROFILE_PIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "profile.png")

# =============================================================================
# REVERSE GEOCODING FUNCTION
# =============================================================================
def get_place_name(lat, lon):
    """Get place name from coordinates using Nominatim (OpenStreetMap)."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'AAVA-DIGIPIN-App/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            display_name = data.get('display_name', '')
            
            # Get the most specific place name available
            place_name = (
                address.get('amenity') or 
                address.get('building') or 
                address.get('house_name') or
                address.get('tourism') or
                address.get('leisure') or
                address.get('office') or
                address.get('shop') or
                address.get('man_made') or
                address.get('road') or
                address.get('neighbourhood') or
                address.get('suburb') or
                address.get('village') or
                address.get('town') or
                address.get('city') or
                'Unknown'
            )
            
            # Get area info
            area = address.get('suburb') or address.get('neighbourhood') or address.get('locality') or ''
            city = address.get('city') or address.get('town') or address.get('village') or address.get('county') or ''
            state = address.get('state') or ''
            
            # Build short address (place + area + city)
            short_parts = [p for p in [place_name, area, city] if p and p != place_name]
            short_address = ', '.join([place_name] + short_parts[:2])
            
            return {
                'place': place_name,
                'short': short_address,
                'full': display_name,
                'area': area,
                'city': city,
                'state': state
            }
    except Exception as e:
        pass
    return None

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
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        width: 280px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 280px !important;
    }
    
    /* Sidebar Navigation - Larger Text */
    [data-testid="stSidebarNav"] ul {
        padding-top: 1rem;
    }
    [data-testid="stSidebarNav"] li {
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebarNav"] a {
        font-size: 1.05rem !important;
        padding: 0.6rem 1rem !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebarNav"] span {
        font-size: 1.05rem !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    
    /* Main container styling */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #2d5a87;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.85rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .metric-delta.positive {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .metric-delta.negative {
        background: #ffebee;
        color: #c62828;
    }
    
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    
    .status-pending { background: #fff3e0; color: #e65100; }
    .status-progress { background: #e3f2fd; color: #1565c0; }
    .status-completed { background: #e8f5e9; color: #2e7d32; }
    .status-failed { background: #ffebee; color: #c62828; }
    
    /* Card container */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e3a5f 0%, #2d5a87 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        border: 1px solid #e0e0e0;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1e3a5f;
        color: white;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
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

tab1, tab2 = st.tabs([
    "📊 Dashboard",
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
                st.caption("📊 Example data - Add validations to see real statistics")
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
        st.caption("📊 Example distribution - Real data will appear as addresses are scored")
    
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
# TAB 2: CONFIDENCE SCORE TESTER
# -----------------------------------------------------------------------------

with tab2:
    st.markdown("### 📈 Confidence Score Calculator")
    st.markdown("""
    Test the confidence score algorithm with custom parameters.
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
        st.markdown("#### 🎲 Test Parameters")
        
        num_deliveries = st.slider(
            "Number of deliveries",
            min_value=1,
            max_value=50,
            value=15,
            key="test_deliveries"
        )
        
        success_rate = st.slider(
            "Delivery success rate",
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.05,
            key="test_success"
        )
        
        num_verifications = st.slider(
            "Number of physical verifications",
            min_value=0,
            max_value=5,
            value=1,
            key="test_verifications"
        )
        
        days_old = st.slider(
            "Days since creation",
            min_value=1,
            max_value=365,
            value=60,
            key="test_days"
        )
    
    if st.button("🔄 Calculate Test Score", type="primary", key="calc_score_btn"):
        # Generate test address
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
