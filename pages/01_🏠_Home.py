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

# Sidebar Navigation CSS - Fix truncation
st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; white-space: nowrap !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; overflow: visible !important; text-overflow: clip !important; }
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

# First row - 4 cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #667eea;">
        <h3 style="margin: 0;">👤</h3>
        <h4 style="margin: 0.5rem 0;">User Portal</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Manage your digital addresses
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_user"):
        st.switch_page("pages/02_👤_User_Portal.py")

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #4CAF50;">
        <h3 style="margin: 0;">✅</h3>
        <h4 style="margin: 0.5rem 0;">Validation Request</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Submit validation requests
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_val"):
        st.switch_page("pages/03_✅_Validation_Request.py")

with col3:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #FF9800;">
        <h3 style="margin: 0;">📊</h3>
        <h4 style="margin: 0.5rem 0;">Confidence Score</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            View address scores
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_score"):
        st.switch_page("pages/04_📊_Confidence_Score.py")

with col4:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #2196F3;">
        <h3 style="margin: 0;">📱</h3>
        <h4 style="margin: 0.5rem 0;">Agent Portal</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Field agent verification
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_agent"):
        st.switch_page("pages/05_📱_Agent_Portal.py")

# Second row - more options
col1, col2, col3, col4 = st.columns(4)

with col1:
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
        st.switch_page("pages/06_⚙️_Admin_Panel.py")

with col2:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #FF5722;">
        <h3 style="margin: 0;">🔗</h3>
        <h4 style="margin: 0.5rem 0;">AIU Access</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Token-based access
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_aiu"):
        st.switch_page("pages/07_🔗_AIU_Access.py")

with col3:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #11998e;">
        <h3 style="margin: 0;">📋</h3>
        <h4 style="margin: 0.5rem 0;">AIP Registry</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Address registry
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_aip"):
        st.switch_page("pages/08_📋_AIP_Registry.py")

with col4:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #1e3a5f;">
        <h3 style="margin: 0;">🗺️</h3>
        <h4 style="margin: 0.5rem 0;">Central Mapper</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            DIGIPIN registry
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_cm"):
        st.switch_page("pages/09_🗺️_Central_Mapper.py")

# Row 3 - Support
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
                border-left: 4px solid #00BCD4;">
        <h3 style="margin: 0;">🤖</h3>
        <h4 style="margin: 0.5rem 0;">AI Chat</h4>
        <p style="color: #666; font-size: 0.9rem; margin: 0;">
            Ask me anything!
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_chat"):
        st.switch_page("pages/10_🤖_AI_Chat.py")

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
    ### DHRUVA Ecosystem (Fully Implemented)
    
    | Component | Role | Page |
    |-----------|------|------|
    | **AIA** | Address Issuance Authority - User consent & address management | 👤 User Portal |
    | **AIP** | Address Information Provider - Address registry & verification | 📚 AIP Registry |
    | **AIU** | Address Information User - Token-based access for services | 🔗 AIU Access |
    | **CM** | Central Mapper - DIGIPIN encoding/decoding registry | 🗺️ Central Mapper |
    
    ### Complete Feature Set
    
    - 👤 **User Portal**: Registration, address management, consent control
    - 📚 **AIP Registry**: Address database, verification tracking, analytics
    - 🔗 **AIU Access**: Token verification, address retrieval for third parties
    - 🗺️ **Central Mapper**: DIGIPIN lookup, encoding, grid reference
    - 📊 **Confidence Scoring**: Multi-factor address quality scoring
    - 📱 **Agent Portal**: Field verification by certified agents
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
