# Home.py
# AAVA - Authorised Address Validation Agency
# Main Entry Point - Combined Home & Dashboard
# 
# Run with: streamlit run Home.py

"""
AAVA - Home
===========
A multi-page Streamlit application for address validation in India's
DHRUVA Digital Address Ecosystem.
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
import requests
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_database, DatabaseManager
from utils.digipin import DIGIPINValidator, encode_digipin, decode_digipin
from utils.confidence_score import (
    ConfidenceScoreCalculator, 
    SampleDataGenerator,
    get_grade_color
)

# =============================================================================
# CONFIG
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

# =============================================================================
# HELPER FUNCTIONS
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
            
            place_name = (
                address.get('amenity') or address.get('building') or 
                address.get('house_name') or address.get('tourism') or
                address.get('road') or address.get('neighbourhood') or
                address.get('suburb') or address.get('city') or 'Unknown'
            )
            
            area = address.get('suburb') or address.get('neighbourhood') or ''
            city = address.get('city') or address.get('town') or address.get('village') or ''
            state = address.get('state') or ''
            
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
    except:
        pass
    return None

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

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="AAVA - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; }
    [data-testid="stSidebar"] > div:first-child { width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; white-space: nowrap !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; overflow: visible !important; text-overflow: clip !important; }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #2d5a87;
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
    
    /* Card */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    /* Quick access card */
    .quick-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# INITIALIZE
# =============================================================================

if 'db' not in st.session_state:
    st.session_state.db = get_database()

if 'digipin_validator' not in st.session_state:
    st.session_state.digipin_validator = DIGIPINValidator()

if 'confidence_calculator' not in st.session_state:
    st.session_state.confidence_calculator = ConfidenceScoreCalculator()

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
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
    except:
        st.info("Loading stats...")
    
    st.divider()
    
    # System info
    st.markdown("### ℹ️ System Info")
    st.markdown(f"""
    - **Version:** 1.0.0
    - **Date:** {datetime.now().strftime('%Y-%m-%d')}
    - **Status:** 🟢 Online
    """)

# =============================================================================
# MAIN HEADER
# =============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">🏠 AAVA</h1>
    <h2 style="margin: 0.5rem 0; font-weight: 400; opacity: 0.9;">
        Authorised Address Validation Agency
    </h2>
    <p style="margin: 1rem 0 0 0; opacity: 0.8;">
        India's Digital Address Ecosystem • DHRUVA Initiative
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN TABS
# =============================================================================

tab1, tab2, tab3 = st.tabs([
    "🚀 Quick Access",
    "📊 Dashboard",
    "📈 Confidence Score Tester"
])

# -----------------------------------------------------------------------------
# TAB 1: QUICK ACCESS
# -----------------------------------------------------------------------------

with tab1:
    st.markdown("### 🚀 Quick Access to All Features")
    
    # Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #667eea;">
            <h3 style="margin: 0;">👤</h3>
            <h4 style="margin: 0.5rem 0;">User Portal</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Manage your digital addresses</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_user", use_container_width=True):
            st.switch_page("pages/01_👤_User_Portal.py")
    
    with col2:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #4CAF50;">
            <h3 style="margin: 0;">✅</h3>
            <h4 style="margin: 0.5rem 0;">Validation Request</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Submit validation requests</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_val", use_container_width=True):
            st.switch_page("pages/02_✅_Validation_Request.py")
    
    with col3:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #FF9800;">
            <h3 style="margin: 0;">📊</h3>
            <h4 style="margin: 0.5rem 0;">Confidence Score</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">View address scores</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_score", use_container_width=True):
            st.switch_page("pages/03_📊_Confidence_Score.py")
    
    with col4:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #2196F3;">
            <h3 style="margin: 0;">📱</h3>
            <h4 style="margin: 0.5rem 0;">Agent Portal</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Field agent verification</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_agent", use_container_width=True):
            st.switch_page("pages/04_📱_Agent_Portal.py")
    
    # Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #9C27B0;">
            <h3 style="margin: 0;">⚙️</h3>
            <h4 style="margin: 0.5rem 0;">Admin Panel</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">System administration</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_admin", use_container_width=True):
            st.switch_page("pages/05_⚙️_Admin_Panel.py")
    
    with col2:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #FF5722;">
            <h3 style="margin: 0;">🔗</h3>
            <h4 style="margin: 0.5rem 0;">AIU Access</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Token-based access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_aiu", use_container_width=True):
            st.switch_page("pages/06_🔗_AIU_Access.py")
    
    with col3:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #11998e;">
            <h3 style="margin: 0;">📋</h3>
            <h4 style="margin: 0.5rem 0;">AIP Registry</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Address registry</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_aip", use_container_width=True):
            st.switch_page("pages/07_📋_AIP_Registry.py")
    
    with col4:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #1e3a5f;">
            <h3 style="margin: 0;">🗺️</h3>
            <h4 style="margin: 0.5rem 0;">Central Mapper</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">DIGIPIN registry</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_cm", use_container_width=True):
            st.switch_page("pages/08_🗺️_Central_Mapper.py")
    
    # Row 3
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="quick-card" style="border-left: 4px solid #00BCD4;">
            <h3 style="margin: 0;">🤖</h3>
            <h4 style="margin: 0.5rem 0;">AI Chat</h4>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Ask me anything!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open →", key="btn_chat", use_container_width=True):
            st.switch_page("pages/09_🤖_AI_Chat.py")
    
    st.divider()
    
    # About Section
    st.markdown("## 📖 About AAVA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### What is AAVA?
        
        **AAVA (Authorised Address Validation Agency)** is a key component of India's 
        **DHRUVA** Digital Public Infrastructure for address management.
        
        AAVA validates addresses through:
        - 📍 **DIGIPIN** validation (10-character geo-codes)
        - ✅ Physical verification by certified agents
        - 📊 Digital verification through delivery feedback
        - 🔒 Privacy-preserving consent management
        
        ### Key Features
        
        - **Confidence Scoring**: 0-100 score based on delivery success, 
          spatial consistency, temporal freshness, and physical verification
        - **Multi-channel Validation**: Physical, Digital, and Hybrid modes
        - **Privacy-First**: Consent-based data access with full audit trails
        """)
    
    with col2:
        st.markdown("""
        ### DHRUVA Ecosystem
        
        | Component | Role |
        |-----------|------|
        | **AIA** | Address Issuance Authority - User consent & address management |
        | **AIP** | Address Information Provider - Address registry & verification |
        | **AIU** | Address Information User - Token-based access for services |
        | **CM** | Central Mapper - DIGIPIN encoding/decoding registry |
        
        ### Complete Feature Set
        
        - 👤 **User Portal**: Registration, address management, consent control
        - 📋 **AIP Registry**: Address database, verification tracking, analytics
        - 🔗 **AIU Access**: Token verification, address retrieval for third parties
        - 🗺️ **Central Mapper**: DIGIPIN lookup, encoding, grid reference
        - 📊 **Confidence Scoring**: Multi-factor address quality scoring
        - 📱 **Agent Portal**: Field verification by certified agents
        """)

# -----------------------------------------------------------------------------
# TAB 2: DASHBOARD
# -----------------------------------------------------------------------------

with tab2:
    st.markdown("### 📊 System Overview")
    
    # Metrics row
    try:
        stats = st.session_state.db.get_dashboard_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Addresses", f"{stats.get('total_addresses', 0):,}",
                     delta="+12 today" if stats.get('total_addresses', 0) > 0 else None)
        with col2:
            st.metric("Total Validations", f"{stats.get('total_validations', 0):,}",
                     delta=f"+{stats.get('validations_today', 0)} today")
        with col3:
            st.metric("Pending", f"{stats.get('pending_validations', 0):,}")
        with col4:
            st.metric("Completed", f"{stats.get('completed_validations', 0):,}")
        with col5:
            avg_conf = stats.get('avg_confidence', 0)
            st.metric("Avg Confidence", f"{avg_conf:.1f}%" if avg_conf else "N/A")
    except:
        st.info("📊 Dashboard metrics will appear once data is available.")
    
    st.divider()
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Validation Status Distribution")
        try:
            val_stats = st.session_state.db.get_validation_stats()
            status_data = val_stats.get('by_status', {})
            
            if not status_data:
                status_data = {'COMPLETED': 45, 'PENDING': 25, 'IN_PROGRESS': 20, 'FAILED': 10}
            
            fig = px.pie(
                values=list(status_data.values()),
                names=list(status_data.keys()),
                color_discrete_sequence=['#4CAF50', '#FF9800', '#2196F3', '#F44336'],
                hole=0.4
            )
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("No validation data available yet.")
    
    with col2:
        st.markdown("#### Confidence Score Distribution")
        np.random.seed(42)
        scores = np.concatenate([
            np.random.normal(85, 8, 30),
            np.random.normal(70, 10, 40),
            np.random.normal(50, 12, 20),
            np.random.normal(35, 8, 10)
        ])
        scores = np.clip(scores, 0, 100)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=scores, nbinsx=20, marker_color='#2d5a87', opacity=0.8))
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300,
                         xaxis_title="Confidence Score", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
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
                    status_class = {'PENDING': 'status-pending', 'IN_PROGRESS': 'status-progress',
                                   'COMPLETED': 'status-completed', 'FAILED': 'status-failed'}.get(val.get('status'), 'status-pending')
                    st.markdown(f"""
                    <div class="card" style="padding: 0.75rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div><strong>{val.get('id', 'N/A')}</strong><br>
                            <span style="color: #666; font-size: 0.85rem;">{val.get('digital_address', val.get('digipin', 'No address'))}</span></div>
                            <span class="status-badge {status_class}">{val.get('status', 'N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No validations yet.")
        except:
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
                            <div><strong>{agent.get('name', 'Unknown')}</strong><br>
                            <span style="color: #666; font-size: 0.85rem;">{agent.get('id', '')}</span></div>
                            <span style="color: {color}; font-weight: 600;">{perf_score:.0f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No agents registered yet.")
        except:
            st.info("No agents to display.")

# -----------------------------------------------------------------------------
# TAB 3: CONFIDENCE SCORE TESTER
# -----------------------------------------------------------------------------

with tab3:
    st.markdown("### 📈 Confidence Score Calculator")
    st.markdown("Test the confidence score algorithm with custom parameters.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📊 Component Weights")
        w1 = st.slider("Delivery Success Rate", 0.0, 1.0, 0.30, 0.05, key="weight_dsr")
        w2 = st.slider("Spatial Consistency", 0.0, 1.0, 0.30, 0.05, key="weight_sc")
        w3 = st.slider("Temporal Freshness", 0.0, 1.0, 0.20, 0.05, key="weight_tf")
        w4 = st.slider("Physical Verification", 0.0, 1.0, 0.20, 0.05, key="weight_pvs")
        
        total_weight = w1 + w2 + w3 + w4
        if abs(total_weight - 1.0) > 0.01:
            st.warning(f"⚠️ Weights sum to {total_weight:.2f} (should be 1.0)")
        else:
            st.success("✅ Weights are valid")
    
    with col2:
        st.markdown("#### 🎲 Test Parameters")
        num_deliveries = st.slider("Number of deliveries", 1, 50, 15, key="test_deliveries")
        success_rate = st.slider("Delivery success rate", 0.0, 1.0, 0.80, 0.05, key="test_success")
        num_verifications = st.slider("Number of physical verifications", 0, 5, 1, key="test_verifications")
        days_old = st.slider("Days since creation", 1, 365, 60, key="test_days")
    
    if st.button("🔄 Calculate Test Score", type="primary", key="calc_score_btn"):
        address = SampleDataGenerator.generate_address(
            num_deliveries=num_deliveries,
            num_verifications=num_verifications,
            success_rate=success_rate
        )
        
        try:
            calculator = ConfidenceScoreCalculator(weights={
                'delivery_success': w1, 'spatial_consistency': w2,
                'temporal_freshness': w3, 'physical_verification': w4
            })
            
            result = calculator.calculate(address)
            
            st.divider()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result.score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confidence Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': get_grade_color(result.grade)},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(244,67,54,0.2)"},
                            {'range': [50, 70], 'color': "rgba(255,193,7,0.2)"},
                            {'range': [70, 90], 'color': "rgba(0,230,118,0.2)"},
                            {'range': [90, 100], 'color': "rgba(0,200,83,0.2)"}
                        ]
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
                grade_class = f"grade-{result.grade.lower().replace('+', '-plus')}"
                st.markdown(f"""
                <div style="text-align: center;">
                    <span class="grade-badge {grade_class}">{result.grade}</span>
                    <p style="margin-top: 0.5rem; color: #666;">{result.grade_description}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("#### 📊 Component Breakdown")
            components_data = []
            for key, comp in result.components.items():
                components_data.append({
                    'Component': comp.name,
                    'Raw Score': f"{comp.raw_value:.2%}",
                    'Weight': f"{comp.weight:.0%}",
                    'Weighted': f"{comp.weighted_value:.4f}"
                })
            st.dataframe(pd.DataFrame(components_data), use_container_width=True, hide_index=True)
            
            if result.recommendations:
                st.markdown("#### 💡 Recommendations")
                for rec in result.recommendations:
                    st.markdown(f"- {rec}")
        except ValueError as e:
            st.error(f"❌ Error: {str(e)}")

# =============================================================================
# DEVELOPER SECTION
# =============================================================================

st.markdown("---")

visitor_count = increment_visitor()

img_base64 = ""
if os.path.exists(PROFILE_PIC):
    try:
        with open(PROFILE_PIC, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
    except:
        pass

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
.dev-flex { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 30px; }
.dev-profile { display: flex; align-items: center; gap: 25px; }
.dev-avatar { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #667eea; object-fit: cover; }
.dev-name { margin: 0 0 3px 0; font-size: 1.3rem; font-weight: 700; color: white; }
.dev-role { margin: 0; opacity: 0.8; font-size: 0.95rem; color: #ddd; }
.dev-footer { margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.dev-links { display: flex; gap: 15px; flex-wrap: wrap; }
.dev-link { padding: 6px 16px; background: rgba(102, 126, 234, 0.3); border-radius: 20px; color: white !important; text-decoration: none; font-size: 0.85rem; border: 1px solid rgba(102, 126, 234, 0.5); }
</style>
""", unsafe_allow_html=True)

avatar_html = f'<img src="data:image/png;base64,{img_base64}" class="dev-avatar">' if img_base64 else '<div class="dev-avatar" style="background:linear-gradient(135deg,#667eea,#764ba2);display:flex;align-items:center;justify-content:center;font-size:2.5rem;">👨‍💻</div>'

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

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; border-top: 1px solid #e0e0e0; margin-top: 2rem;">
    <p><strong>AAVA</strong> - Authorised Address Validation Agency<br>
    Part of India's DHRUVA Digital Address Ecosystem</p>
</div>
""", unsafe_allow_html=True)
