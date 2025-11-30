# pages/1_🏠_Home.py
# AAVA - Home/Landing Page
# Provides overview and quick access to all features

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.premium_theme import PREMIUM_CSS, PAGE_GRADIENTS

st.set_page_config(
    page_title="Home - AAVA",
    page_icon="🏠",
    layout="wide"
)

# Apply premium theme
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# Premium Header
st.markdown(f"""
<div class="premium-header" style="background: linear-gradient(135deg, {PAGE_GRADIENTS['home'][0]} 0%, {PAGE_GRADIENTS['home'][1]} 50%, {PAGE_GRADIENTS['home'][2]} 100%); text-align: center;">
    <h1 style="margin: 0; font-size: 2.5rem; display: flex; align-items: center; justify-content: center; gap: 15px;">
        <span>🏠</span> AAVA
    </h1>
    <h2 style="margin: 0.75rem 0; font-weight: 500; font-size: 1.3rem; opacity: 0.95;">
        Authorised Address Validation Agency
    </h2>
    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
        India's Digital Address Ecosystem • DHRUVA Initiative
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; font-size: 0.85rem;">⚡ Real-time</span>
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; font-size: 0.85rem;">🔒 Secure</span>
        <span style="background: rgba(255,255,255,0.2); padding: 6px 16px; border-radius: 20px; font-size: 0.85rem;">🇮🇳 Pan-India</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Feature cards section
st.markdown('<h2 style="color: #ffffff; font-size: 1.5rem; margin: 2rem 0 1.5rem 0;">🚀 Quick Access</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card" style="border-left: 4px solid #00e676;">
        <div class="icon">✅</div>
        <h4 style="color: #ffffff; font-size: 1.1rem;">Validation Request</h4>
        <p style="color: #b8c5d6; font-size: 0.9rem;">Submit validation requests</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_val", use_container_width=True):
        st.switch_page("pages/2_✅_Validation_Request.py")

with col2:
    st.markdown("""
    <div class="feature-card" style="border-left: 4px solid #2196F3;">
        <div class="icon">📱</div>
        <h4 style="color: #ffffff; font-size: 1.1rem;">Agent Portal</h4>
        <p style="color: #b8c5d6; font-size: 0.9rem;">Field verification portal</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_agent", use_container_width=True):
        st.switch_page("pages/3_📱_Agent_Portal.py")

with col3:
    st.markdown("""
    <div class="feature-card" style="border-left: 4px solid #FF9800;">
        <div class="icon">📊</div>
        <h4 style="color: #ffffff; font-size: 1.1rem;">Confidence Score</h4>
        <p style="color: #b8c5d6; font-size: 0.9rem;">View confidence scores</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_score", use_container_width=True):
        st.switch_page("pages/4_📊_Confidence_Score.py")

with col4:
    st.markdown("""
    <div class="feature-card" style="border-left: 4px solid #9C27B0;">
        <div class="icon">⚙️</div>
        <h4 style="color: #ffffff; font-size: 1.1rem;">Admin Panel</h4>
        <p style="color: #b8c5d6; font-size: 0.9rem;">System administration</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open →", key="btn_admin", use_container_width=True):
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
