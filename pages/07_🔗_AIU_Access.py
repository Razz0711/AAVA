# pages/8_🔗_AIU_Access.py
# AAVA - AIU (Address Information User) Access Portal
# Third-party organizations use access tokens to retrieve address information

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager

st.set_page_config(
    page_title="AIU Access - AAVA",
    page_icon="🔗",
    layout="wide"
)

# Initialize
db = DatabaseManager()
db.initialize()

# CSS
st.markdown("""
<style>
    /* Wider sidebar to prevent truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] span { overflow: visible !important; text-overflow: clip !important; }
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #dee2e6;
    }
    .info-label {
        color: #666;
        font-weight: 500;
    }
    .info-value {
        font-weight: 600;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%); 
            padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <h1 style="margin: 0;">🔗 AIU Access Portal</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        Address Information User • Retrieve Address Data with Consent Token
    </p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
### What is AIU Access?

**Address Information Users (AIUs)** are organizations that need to access verified address 
information with user consent. This includes:

- 🏦 **Banks & Financial Institutions** - KYC verification
- 📱 **Telecom Providers** - SIM card address verification
- 🛒 **E-commerce Platforms** - Delivery address validation
- 🏛️ **Government Agencies** - Identity and address verification
- 🏥 **Healthcare Providers** - Patient address verification

### How it Works

1. **User Grants Access**: User shares their address via the User Portal
2. **Token Generated**: A unique access token is created
3. **AIU Retrieves Data**: Use the token below to access address details
4. **Access Logged**: All accesses are logged for user transparency
""")

st.markdown("---")

# Token Input Section
st.markdown("## 🔑 Enter Access Token")

col1, col2 = st.columns([3, 1])

with col1:
    access_token = st.text_input(
        "Access Token",
        placeholder="Paste the access token provided by the user...",
        help="This token was generated when the user shared their address with your organization"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    verify_btn = st.button("🔍 Verify & Retrieve", use_container_width=True, type="primary")

# Process token
if verify_btn and access_token:
    with st.spinner("Verifying token and retrieving address..."):
        consent = db.get_consent_by_token(access_token.strip())
        
        if consent:
            # Success - Show address details
            st.markdown("""
            <div class="success-card">
                <h3 style="color: #28a745; margin: 0;">✅ Token Verified Successfully</h3>
                <p style="margin: 0.5rem 0 0 0; color: #155724;">
                    Access granted. Address details retrieved below.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Consent Info
            st.markdown("### 📋 Consent Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Consent ID:** `{consent.get('id')}`")
                st.markdown(f"**Purpose:** {consent.get('purpose', 'N/A')}")
            with col2:
                st.markdown(f"**Scope:** {consent.get('scope', 'view').upper()}")
                st.markdown(f"**Expires:** {consent.get('expires_at', 'Never')[:10] if consent.get('expires_at') else 'Never'}")
            with col3:
                st.markdown(f"**Access Count:** {consent.get('access_count', 0)}")
                st.markdown(f"**Granted:** {consent.get('issued_at', 'N/A')[:10] if consent.get('issued_at') else 'N/A'}")
            
            st.markdown("---")
            
            # Address Details
            st.markdown("### 📍 Address Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Core Information")
                
                # DIGIPIN
                digipin = consent.get('digipin', 'N/A')
                formatted_digipin = f"{digipin[:3]}-{digipin[3:6]}-{digipin[6:]}" if len(digipin) == 10 else digipin
                st.markdown(f"""
                <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span style="color: #1565c0; font-weight: 500;">DIGIPIN</span><br>
                    <span style="font-size: 1.5rem; font-weight: bold; font-family: monospace;">{formatted_digipin}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Digital Address
                if consent.get('digital_address'):
                    st.markdown(f"**Digital Address:** {consent.get('digital_address')}")
                
                # Descriptive Address
                st.markdown(f"**Descriptive Address:**")
                st.info(consent.get('descriptive_address', 'N/A'))
                
                # Location Details
                st.markdown(f"**City:** {consent.get('city', 'N/A')}")
                st.markdown(f"**State:** {consent.get('state', 'N/A')}")
                st.markdown(f"**PIN Code:** {consent.get('pincode', 'N/A')}")
            
            with col2:
                st.markdown("#### Location & Verification")
                
                # Coordinates
                lat = consent.get('latitude')
                lon = consent.get('longitude')
                
                if lat and lon:
                    st.markdown(f"**Coordinates:** {lat:.6f}, {lon:.6f}")
                    
                    # Show map
                    import pandas as pd
                    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                    st.map(map_data, zoom=15)
                
                # Confidence Score
                score = consent.get('confidence_score', 0)
                grade = consent.get('confidence_grade', 'F')
                grade_color = {
                    'A': '#28a745', 'B': '#5cb85c', 'C': '#ffc107', 
                    'D': '#fd7e14', 'F': '#dc3545'
                }.get(grade, '#6c757d')
                
                st.markdown(f"""
                <div style="background: {grade_color}20; padding: 1rem; border-radius: 8px; 
                            border: 2px solid {grade_color}; text-align: center; margin-top: 1rem;">
                    <span style="color: #666;">Confidence Score</span><br>
                    <span style="font-size: 2rem; font-weight: bold; color: {grade_color};">{grade}</span><br>
                    <span style="font-size: 1.2rem; font-weight: 600;">{score:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Export Options
            st.markdown("---")
            st.markdown("### 📤 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            # JSON Export
            import json
            export_data = {
                "consent_id": consent.get('id'),
                "digipin": consent.get('digipin'),
                "digital_address": consent.get('digital_address'),
                "descriptive_address": consent.get('descriptive_address'),
                "city": consent.get('city'),
                "state": consent.get('state'),
                "pincode": consent.get('pincode'),
                "latitude": consent.get('latitude'),
                "longitude": consent.get('longitude'),
                "confidence_score": consent.get('confidence_score'),
                "confidence_grade": consent.get('confidence_grade'),
                "retrieved_at": datetime.now().isoformat(),
                "scope": consent.get('scope'),
                "expires_at": consent.get('expires_at')
            }
            
            with col1:
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"address_{consent.get('digipin', 'data')}.json",
                    mime="application/json"
                )
            
            # Note about usage
            st.markdown("""
            <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <strong>⚠️ Usage Notice:</strong> This address data is provided under user consent 
                for the stated purpose only. Unauthorized use, storage, or sharing is prohibited 
                under India's Digital Personal Data Protection Act.
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Error - Invalid token
            st.markdown("""
            <div class="error-card">
                <h3 style="color: #dc3545; margin: 0;">❌ Token Invalid or Expired</h3>
                <p style="margin: 0.5rem 0 0 0; color: #721c24;">
                    The access token could not be verified. Please check the following:
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            ### Possible Reasons:
            
            1. **Token Expired**: The consent may have reached its expiry date
            2. **Token Revoked**: The user may have revoked access
            3. **Invalid Token**: The token may be incorrect or corrupted
            4. **Token Not Found**: The token does not exist in our system
            
            ### What to Do:
            
            - Double-check the token for any typos
            - Contact the user to request a new access token
            - Ensure the token hasn't been revoked by the user
            """)

elif verify_btn and not access_token:
    st.warning("⚠️ Please enter an access token")

# Information Section
st.markdown("---")
st.markdown("## 📚 API Integration Guide")

with st.expander("🔧 For Developers - REST API Access"):
    st.markdown("""
    ### REST API Endpoint
    
    For programmatic access, you can use our REST API:
    
    ```
    GET /api/v1/address/verify
    Headers:
      Authorization: Bearer <access_token>
      X-AIU-ID: <your_aiu_id>
    ```
    
    ### Response Format
    
    ```json
    {
      "success": true,
      "data": {
        "digipin": "3PJK4M5L2T",
        "digital_address": "user@provider.in",
        "descriptive_address": "...",
        "city": "New Delhi",
        "state": "Delhi",
        "pincode": "110001",
        "coordinates": {
          "latitude": 28.6139,
          "longitude": 77.2090
        },
        "confidence": {
          "score": 85,
          "grade": "A"
        }
      },
      "consent": {
        "id": "CON-XXXXXXXX",
        "scope": "view",
        "expires_at": "2024-12-31T23:59:59"
      }
    }
    ```
    
    ### Rate Limits
    
    - 100 requests per minute per AIU
    - 10,000 requests per day per AIU
    
    ### Error Codes
    
    | Code | Description |
    |------|-------------|
    | 401 | Invalid or expired token |
    | 403 | Consent revoked |
    | 404 | Address not found |
    | 429 | Rate limit exceeded |
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    <p>🔒 All access is logged and audited for user transparency</p>
    <p>AAVA - Address Information User (AIU) Portal • DHRUVA Initiative</p>
</div>
""", unsafe_allow_html=True)
