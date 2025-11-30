# pages/2_✅_Validation_Request.py
# AAVA - Validation Request Page
# Submit new address validation requests

import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.digipin import DIGIPINValidator
from utils.premium_theme import PREMIUM_CSS, PAGE_GRADIENTS

st.set_page_config(
    page_title="Validation Request - AAVA",
    page_icon="✅",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()

# Apply Premium Theme
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# Premium Header
st.markdown(f"""
<div class="premium-header" style="background: linear-gradient(135deg, {PAGE_GRADIENTS['validation'][0]} 0%, {PAGE_GRADIENTS['validation'][1]} 50%, {PAGE_GRADIENTS['validation'][2]} 100%);">
    <h1 style="margin: 0; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 2rem;">✅</span> Validation Request
    </h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">Submit a new address validation request</p>
</div>
""", unsafe_allow_html=True)

# Tabs for different views
tab1, tab2 = st.tabs(["📝 New Request", "📋 My Requests"])

# -----------------------------------------------------------------------------
# TAB 1: NEW REQUEST FORM
# -----------------------------------------------------------------------------

with tab1:
    st.markdown("### Submit New Validation Request")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Address Information Section
        st.markdown("#### 📍 Address Information")
        
        digital_address = st.text_input(
            "Digital Address (optional)",
            placeholder="username@provider.in",
            help="UPI-like digital address identifier"
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            digipin = st.text_input(
                "DIGIPIN *",
                placeholder="XXX-XXX-XXXX",
                help="10-character DIGIPIN code"
            ).upper()
            
            # Validate DIGIPIN in real-time
            if digipin:
                is_valid, message = validator.validate_with_details(digipin)
                if is_valid:
                    result = validator.decode(digipin)
                    st.success(f"✅ Valid DIGIPIN - Location: ({result.center_lat:.4f}, {result.center_lon:.4f})")
                else:
                    st.error(f"❌ {message}")
        
        with col_b:
            pincode = st.text_input(
                "PIN Code",
                placeholder="110001",
                max_chars=6
            )
        
        descriptive_address = st.text_area(
            "Descriptive Address *",
            placeholder="Enter the complete address with landmarks...",
            height=100,
            help="Full address including building, street, locality, city, state"
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            city = st.text_input("City", placeholder="New Delhi")
        
        with col_b:
            state = st.selectbox(
                "State/UT",
                options=[
                    "", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
                    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
                    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
                    "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
                    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
                    "Uttar Pradesh", "Uttarakhand", "West Bengal",
                    "Delhi", "Jammu and Kashmir", "Ladakh", "Puducherry",
                    "Chandigarh", "Andaman and Nicobar", "Dadra and Nagar Haveli",
                    "Daman and Diu", "Lakshadweep"
                ]
            )
        
        st.divider()
        
        # Validation Settings
        st.markdown("#### ⚙️ Validation Settings")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            validation_type = st.selectbox(
                "Validation Type *",
                options=["DIGITAL", "PHYSICAL", "HYBRID"],
                index=2,
                help="""
                - DIGITAL: Query-based validation only
                - PHYSICAL: On-site verification by agent
                - HYBRID: Digital first, physical if needed
                """
            )
        
        with col_b:
            priority = st.selectbox(
                "Priority",
                options=["LOW", "NORMAL", "HIGH", "URGENT"],
                index=1
            )
        
        # Purpose/Scope
        validation_purpose = st.multiselect(
            "Validation Purpose",
            options=[
                "Delivery Verification",
                "KYC/Identity Verification",
                "Service Installation",
                "Financial Services",
                "Government Services",
                "Other"
            ],
            default=["Delivery Verification"]
        )
        
        notes = st.text_area(
            "Additional Notes (optional)",
            placeholder="Any special instructions or information...",
            height=80
        )
        
        st.divider()
        
        # Consent Section
        st.markdown("#### 🔒 Consent & Authorization")
        
        st.markdown("""
        <div class="info-box">
            <strong>Privacy Notice:</strong> Your address data will be processed 
            according to India's Digital Personal Data Protection Act. Data will only 
            be used for the specified validation purpose and shared with authorized 
            parties with your consent.
        </div>
        """, unsafe_allow_html=True)
        
        consent_1 = st.checkbox(
            "I consent to the collection and processing of my address data for validation purposes",
            key="consent_1"
        )
        
        consent_2 = st.checkbox(
            "I authorize AAVA to share validation results with the requesting party",
            key="consent_2"
        )
        
        consent_3 = st.checkbox(
            "I confirm that the address information provided is accurate to the best of my knowledge",
            key="consent_3"
        )
        
        all_consents = consent_1 and consent_2 and consent_3
        
        st.divider()
        
        # Submit Button
        col_submit, col_clear = st.columns([1, 4])
        
        with col_submit:
            submit_btn = st.button(
                "🚀 Submit Request",
                type="primary",
                disabled=not all_consents,
                use_container_width=True
            )
        
        if not all_consents:
            st.warning("⚠️ Please provide all required consents to submit the request.")
        
        if submit_btn and all_consents:
            # Validate required fields
            if not digipin or not descriptive_address:
                st.error("❌ Please fill in all required fields (DIGIPIN and Descriptive Address)")
            elif not validator.validate(digipin):
                st.error("❌ Please enter a valid DIGIPIN")
            else:
                # Create consent artifact
                consent_id = f"CON-{str(uuid.uuid4())[:8].upper()}"
                consent_data = {
                    'id': consent_id,
                    'subject_id': digital_address or 'anonymous',
                    'granter': 'user',
                    'grantee': 'AAVA',
                    'scope': validation_purpose,
                    'consent_artifact': json.dumps({
                        'version': '1.0',
                        'granted_at': datetime.now().isoformat(),
                        'consents': {
                            'data_collection': consent_1,
                            'result_sharing': consent_2,
                            'accuracy_confirmation': consent_3
                        }
                    }),
                    'expires_at': (datetime.now() + timedelta(days=180)).isoformat()
                }
                
                try:
                    # Store consent
                    db.create_consent(consent_data)
                    
                    # Decode DIGIPIN for coordinates
                    digipin_result = validator.decode(digipin)
                    
                    # Create address record if it doesn't exist
                    existing_address = db.get_address_by_digipin(digipin)
                    
                    if existing_address:
                        address_id = existing_address['id']
                    else:
                        address_id = db.create_address({
                            'digital_address': digital_address,
                            'digipin': digipin.replace('-', ''),
                            'descriptive_address': descriptive_address,
                            'latitude': digipin_result.center_lat,
                            'longitude': digipin_result.center_lon,
                            'city': city,
                            'state': state,
                            'pincode': pincode
                        })
                    
                    # Create validation request
                    validation_id = db.create_validation({
                        'address_id': address_id,
                        'digital_address': digital_address,
                        'digipin': digipin.replace('-', ''),
                        'descriptive_address': descriptive_address,
                        'validation_type': validation_type,
                        'status': 'PENDING',
                        'priority': priority,
                        'consent_id': consent_id,
                        'notes': notes
                    })
                    
                    # Log audit
                    db.log_audit({
                        'actor': 'user',
                        'action': 'validation.created',
                        'resource_type': 'validation',
                        'resource_id': validation_id,
                        'details': {
                            'type': validation_type,
                            'priority': priority
                        }
                    })
                    
                    # Success message
                    st.markdown(f"""
                    <div class="success-card">
                        <h3 style="margin: 0; color: #2e7d32;">✅ Request Submitted Successfully!</h3>
                        <p style="margin: 1rem 0;">Your validation request has been created.</p>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Request ID:</strong></td>
                                <td><code>{validation_id}</code></td>
                            </tr>
                            <tr>
                                <td><strong>Consent ID:</strong></td>
                                <td><code>{consent_id}</code></td>
                            </tr>
                            <tr>
                                <td><strong>Type:</strong></td>
                                <td>{validation_type}</td>
                            </tr>
                            <tr>
                                <td><strong>Priority:</strong></td>
                                <td>{priority}</td>
                            </tr>
                            <tr>
                                <td><strong>Status:</strong></td>
                                <td>PENDING</td>
                            </tr>
                        </table>
                        <p style="margin-top: 1rem; color: #666;">
                            You will receive updates as the validation progresses.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Store in session for tracking
                    if 'my_validations' not in st.session_state:
                        st.session_state.my_validations = []
                    st.session_state.my_validations.append(validation_id)
                    
                except Exception as e:
                    st.error(f"❌ Error submitting request: {str(e)}")
    
    with col2:
        # Information Panel
        st.markdown("#### ℹ️ Information")
        
        with st.expander("📍 About DIGIPIN", expanded=True):
            st.markdown("""
            DIGIPIN is a 10-character geo-coded address:
            - Format: `XXX-XXX-XXXX`
            - Represents a ~4m × 4m area
            - Characters: `2-9, C, F, J, K, L, M, P, T`
            
            **Example:** `3PJ-K4M-5L2T`
            """)
        
        with st.expander("📋 Validation Types"):
            st.markdown("""
            **DIGITAL** 
            - Query-based verification
            - Uses delivery history, spatial data
            - Fastest (minutes)
            
            **PHYSICAL**
            - On-site agent verification
            - Photo evidence, GPS confirmation
            - 24-48 hours typical
            
            **HYBRID** (Recommended)
            - Starts with digital
            - Escalates to physical if needed
            - Best accuracy
            """)
        
        with st.expander("🔒 Privacy & Consent"):
            st.markdown("""
            Your data is protected under:
            - Digital Personal Data Protection Act
            - DHRUVA Privacy Framework
            
            **Your Rights:**
            - Access your data
            - Revoke consent
            - Request deletion
            - Data portability
            """)
        
        with st.expander("⏱️ Expected Timeline"):
            st.markdown("""
            | Priority | Digital | Physical |
            |----------|---------|----------|
            | Low | 24h | 5-7 days |
            | Normal | 4h | 2-3 days |
            | High | 1h | 24h |
            | Urgent | 15m | 4-6h |
            """)


# -----------------------------------------------------------------------------
# TAB 2: MY REQUESTS
# -----------------------------------------------------------------------------

with tab2:
    st.markdown("### 📋 My Validation Requests")
    
    # Search/Filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by ID or Address",
            placeholder="Enter validation ID or address..."
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All", "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"]
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Refresh", use_container_width=True)
    
    # Get validations
    try:
        if status_filter == "All":
            validations = db.get_all_validations(limit=50)
        else:
            validations = db.get_validations_by_status(status_filter)
        
        if search_query:
            search_lower = search_query.lower()
            validations = [
                v for v in validations
                if search_lower in v.get('id', '').lower()
                or search_lower in (v.get('digital_address') or '').lower()
                or search_lower in (v.get('digipin') or '').lower()
            ]
        
        if validations:
            # Display as cards
            for val in validations:
                status = val.get('status', 'PENDING')
                status_color = {
                    'PENDING': '#ff9800',
                    'IN_PROGRESS': '#2196f3',
                    'COMPLETED': '#4caf50',
                    'FAILED': '#f44336',
                    'CANCELLED': '#9e9e9e'
                }.get(status, '#9e9e9e')
                
                priority = val.get('priority', 'NORMAL')
                priority_color = {
                    'LOW': '#9e9e9e',
                    'NORMAL': '#2196f3',
                    'HIGH': '#ff9800',
                    'URGENT': '#f44336'
                }.get(priority, '#2196f3')
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 8px; 
                                box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 0.5rem;
                                border-left: 4px solid {status_color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1rem;">{val.get('id', 'N/A')}</strong>
                                <span style="background: {status_color}; color: white; 
                                            padding: 0.2rem 0.5rem; border-radius: 4px; 
                                            font-size: 0.75rem; margin-left: 0.5rem;">
                                    {status}
                                </span>
                                <span style="background: {priority_color}; color: white; 
                                            padding: 0.2rem 0.5rem; border-radius: 4px; 
                                            font-size: 0.75rem; margin-left: 0.25rem;">
                                    {priority}
                                </span>
                            </div>
                            <span style="color: #666; font-size: 0.85rem;">
                                {val.get('validation_type', 'DIGITAL')}
                            </span>
                        </div>
                        <div style="margin-top: 0.5rem; color: #666;">
                            <div>📍 {val.get('digipin', 'No DIGIPIN')}</div>
                            <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                                {(val.get('descriptive_address') or 'No address')[:60]}...
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #999;">
                            Created: {val.get('created_at', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("View Details", key=f"view_{val.get('id')}"):
                        st.session_state.selected_validation = val.get('id')
                        st.rerun()
            
            # Show selected validation details
            if 'selected_validation' in st.session_state:
                val_id = st.session_state.selected_validation
                val_details = db.get_validation(val_id)
                
                if val_details:
                    st.divider()
                    st.markdown(f"### Validation Details: {val_id}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.json(val_details)
                    
                    with col2:
                        # Get related verifications
                        verifications = db.get_verifications_by_validation(val_id)
                        
                        if verifications:
                            st.markdown("#### Verifications")
                            for ver in verifications:
                                st.markdown(f"""
                                - **{ver.get('id')}**: 
                                  {'✅ Verified' if ver.get('verified') else '❌ Not Verified'}
                                  (Quality: {ver.get('quality_score', 0):.0%})
                                """)
                        else:
                            st.info("No verifications yet")
                        
                        if st.button("Close Details"):
                            del st.session_state.selected_validation
                            st.rerun()
        
        else:
            st.info("📋 No validation requests found. Submit a new request to get started!")
    
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    AAVA • Address Validation Agency • DHRUVA Ecosystem
</div>
""", unsafe_allow_html=True)
