# pages/1_🏠_Home.py
# AAVA - Home/Landing Page
# Provides overview and quick access to all features

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Home - AAVA",
    page_icon="🏠",
    layout="wide"
)

# Sidebar Navigation CSS
st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); 
            padding: 3rem 2rem; border-radius: 12px; color: white; 
            text-align: center; margin-bottom: 2rem;">
    <h1 style="margin: 0; font-size: 2.5rem;">🏠 AAVA</h1>
    <h2 style="margin: 0.5rem 0; font-weight: 400; opacity: 0.9;">
        Authorised Address Validation Agency
    </h2>
    <p style="margin: 1rem 0 0 0; opacity: 0.8;">
        India's Digital Address Ecosystem • DHRUVA Initiative
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
st.markdown("## 🚀 Quick Access")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #4CAF50;">
        <h3 style="margin: 0;">✅</h3>
        <h4 style="margin: 0.5rem 0;">Validation Request</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Submit new address validation requests
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_val"):
        st.switch_page("pages/2_✅_Validation_Request.py")

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #2196F3;">
        <h3 style="margin: 0;">📱</h3>
        <h4 style="margin: 0.5rem 0;">Agent Portal</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Field agent verification portal
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_agent"):
        st.switch_page("pages/3_📱_Agent_Portal.py")

with col3:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #FF9800;">
        <h3 style="margin: 0;">📊</h3>
        <h4 style="margin: 0.5rem 0;">Confidence Score</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            View address confidence scores
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_score"):
        st.switch_page("pages/4_📊_Confidence_Score.py")

with col4:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #9C27B0;">
        <h3 style="margin: 0;">⚙️</h3>
        <h4 style="margin: 0.5rem 0;">Admin Panel</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            System administration
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_admin"):
        st.switch_page("pages/5_⚙️_Admin_Panel.py")

st.divider()

# About section
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
    - **Quality Assurance**: Agent certification and fraud detection
    """)

with col2:
    st.markdown("""
    ### DHRUVA Ecosystem
    
    AAVA integrates with these DHRUVA components:
    
    | Component | Role |
    |-----------|------|
    | **AIA** | Address Information Agent (field verification) |
    | **AIP** | Address Information Provider (address registry) |
    | **AIU** | Address Information User (service consumers) |
    | **CM** | Central Mapper (DIGIPIN registry) |
    
    ### DIGIPIN System
    
    DIGIPIN is a 10-character geo-coded grid system:
    - Covers all of India (2.5°-38.5°N, 63.5°-99.5°E)
    - ~4m × 4m resolution at finest level
    - Format: `XXX-XXX-XXXX` (e.g., `3PJ-K4M-5L2T`)
    - Uses 16 characters: `2,3,4,5,6,7,8,9,C,F,J,K,L,M,P,T`
    """)

st.divider()

# Stats preview
st.markdown("## 📈 System Status")

try:
    from utils.database import get_database
    db = get_database()
    stats = db.get_dashboard_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Addresses", f"{stats.get('total_addresses', 0):,}")
    with col2:
        st.metric("Total Validations", f"{stats.get('total_validations', 0):,}")
    with col3:
        st.metric("Pending", f"{stats.get('pending_validations', 0):,}")
    with col4:
        st.metric("Active Agents", f"{stats.get('active_agents', 0):,}")
    with col5:
        avg = stats.get('avg_confidence', 0)
        st.metric("Avg Confidence", f"{avg:.1f}%" if avg else "N/A")

except Exception as e:
    st.info("📊 System statistics will appear once data is available.")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>AAVA • DHRUVA Digital Address Ecosystem • India</p>
</div>
""", unsafe_allow_html=True)
