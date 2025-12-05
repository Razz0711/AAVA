# pages/7_👤_User_Portal.py
# AAVA - User Portal (AIA - Address Issuance Authority)
# User registration, login, address management, and consent control

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager
from utils.digipin import DIGIPINValidator

st.set_page_config(
    page_title="User Portal - AAVA",
    page_icon="👤",
    layout="wide"
)

# Initialize
db = DatabaseManager()
db.initialize()
digipin_validator = DIGIPINValidator()

# CSS
st.markdown("""
<style>
    /* Wider sidebar to prevent truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] span { overflow: visible !important; text-overflow: clip !important; }
    .user-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .address-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }
    .consent-card {
        background: #fff3cd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    .consent-card.revoked {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .consent-card.active {
        background: #d4edda;
        border-left: 4px solid #28a745;
    }
    .stat-box {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <h1 style="margin: 0;">👤 User Portal</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        AIA - Address Issuance Authority • Manage Your Digital Addresses
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# ============================================================================
# AUTHENTICATION SECTION
# ============================================================================

def show_login_register():
    """Show login and registration forms."""
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        with st.form("login_form"):
            email = st.text_input("📧 Email Address")
            password = st.text_input("🔑 Password", type="password")
            login_btn = st.form_submit_button("Login", use_container_width=True)
            
            if login_btn:
                if email and password:
                    user = db.authenticate_user(email, password)
                    if user:
                        st.session_state.logged_in_user = user
                        st.success(f"✅ Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
                else:
                    st.warning("⚠️ Please enter email and password")
    
    with tab2:
        st.markdown("### Create New Account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Full Name*")
                email = st.text_input("📧 Email Address*")
            with col2:
                phone = st.text_input("📱 Phone Number")
                password = st.text_input("🔑 Create Password*", type="password")
            
            confirm_password = st.text_input("🔑 Confirm Password*", type="password")
            
            st.markdown("---")
            agree = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            register_btn = st.form_submit_button("Create Account", use_container_width=True)
            
            if register_btn:
                if not name or not email or not password:
                    st.error("❌ Please fill all required fields")
                elif password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                elif not agree:
                    st.warning("⚠️ Please agree to the Terms of Service")
                else:
                    try:
                        user_id = db.create_user({
                            'name': name,
                            'email': email,
                            'phone': phone if phone else None,
                            'password': password
                        })
                        st.success(f"✅ Account created! Your User ID: {user_id}")
                        st.info("You can now login with your email and password")
                    except ValueError as e:
                        st.error(f"❌ {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error creating account: {str(e)}")


# ============================================================================
# MAIN USER DASHBOARD
# ============================================================================

def show_user_dashboard():
    """Show main user dashboard after login."""
    user = st.session_state.logged_in_user
    
    # Sidebar - User Info
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1rem; border-radius: 8px; color: white; text-align: center;">
            <h3 style="margin: 0;">👤 {user['name']}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">{user['email']}</p>
            <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">ID: {user['id']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()
    
    # Get user data
    user_addresses = db.get_user_addresses(user['id'])
    user_consents = db.get_user_consents(user['id'])
    active_consents = [c for c in user_consents if not c.get('revoked')]
    
    # Stats Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h2 style="margin: 0;">{len(user_addresses)}</h2>
            <p style="margin: 0; opacity: 0.9;">My Addresses</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <h2 style="margin: 0;">{len(active_consents)}</h2>
            <p style="margin: 0; opacity: 0.9;">Active Consents</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_access = sum(c.get('access_count', 0) for c in user_consents)
        st.markdown(f"""
        <div class="stat-box">
            <h2 style="margin: 0;">{total_access}</h2>
            <p style="margin: 0; opacity: 0.9;">Total Accesses</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        verified_count = len([a for a in user_addresses if a.get('confidence_score', 0) > 70])
        st.markdown(f"""
        <div class="stat-box">
            <h2 style="margin: 0;">{verified_count}</h2>
            <p style="margin: 0; opacity: 0.9;">Verified Addresses</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 My Addresses", 
        "➕ Add Address", 
        "🔐 Consent Management",
        "📜 Access History"
    ])
    
    # ========== TAB 1: MY ADDRESSES ==========
    with tab1:
        st.markdown("### 🏠 My Digital Addresses")
        
        if not user_addresses:
            st.info("📭 You haven't added any addresses yet. Go to 'Add Address' tab to add one!")
        else:
            for addr in user_addresses:
                primary_badge = "⭐ PRIMARY" if addr.get('is_primary') else ""
                grade = addr.get('confidence_grade', 'F')
                grade_color = {
                    'A': '#28a745', 'B': '#5cb85c', 'C': '#ffc107', 
                    'D': '#fd7e14', 'F': '#dc3545'
                }.get(grade, '#6c757d')
                
                with st.expander(f"📍 {addr.get('label', 'Address')} - {addr.get('digipin', 'N/A')} {primary_badge}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **DIGIPIN:** `{addr.get('digipin', 'N/A')}`  
                        **Digital Address:** {addr.get('digital_address', 'N/A')}  
                        **Descriptive:** {addr.get('descriptive_address', 'N/A')}  
                        **Location:** {addr.get('city', '')}, {addr.get('state', '')} - {addr.get('pincode', '')}
                        """)
                        
                        if addr.get('latitude') and addr.get('longitude'):
                            st.markdown(f"**Coordinates:** {addr['latitude']:.6f}, {addr['longitude']:.6f}")
                    
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: {grade_color}20; 
                                    border-radius: 8px; border: 2px solid {grade_color};">
                            <h1 style="margin: 0; color: {grade_color};">{grade}</h1>
                            <p style="margin: 0; font-size: 0.85rem;">Confidence Grade</p>
                            <p style="margin: 0; font-weight: bold;">{addr.get('confidence_score', 0):.0f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Check if there's a pending validation for this address
                    pending_validation = db.get_pending_validation_for_address(addr['address_id'])
                    
                    # Actions
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if not addr.get('is_primary'):
                            if st.button("⭐ Set Primary", key=f"primary_{addr['address_id']}"):
                                db.update_user_address(user['id'], addr['address_id'], {'is_primary': 1})
                                st.success("✅ Set as primary address!")
                                st.rerun()
                    with col2:
                        new_label = st.text_input("Label", value=addr.get('label', 'Home'), 
                                                  key=f"label_{addr['address_id']}")
                        if new_label != addr.get('label'):
                            if st.button("Update Label", key=f"upd_label_{addr['address_id']}"):
                                db.update_user_address(user['id'], addr['address_id'], {'label': new_label})
                                st.rerun()
                    with col3:
                        if st.button("🔗 Share Address", key=f"share_{addr['address_id']}"):
                            st.session_state[f"show_share_{addr['address_id']}"] = True
                    with col4:
                        # Show verification status or button
                        if pending_validation:
                            # Show pending status instead of button
                            status = pending_validation.get('status', 'PENDING')
                            if status == 'PENDING':
                                st.warning("⏳ Pending")
                            elif status == 'IN_PROGRESS':
                                st.info("🔄 In Progress")
                        elif addr.get('confidence_score', 0) >= 70:
                            # Already verified with good score
                            st.success("✅ Verified")
                        else:
                            # Show verify button
                            if st.button("✅ Verify", key=f"verify_{addr['address_id']}", type="primary"):
                                validation_id = db.create_validation({
                                    'address_id': addr['address_id'],
                                    'digital_address': addr.get('digital_address'),
                                    'digipin': addr.get('digipin'),
                                    'descriptive_address': addr.get('descriptive_address'),
                                    'validation_type': 'PHYSICAL',
                                    'status': 'PENDING',
                                    'priority': 'NORMAL',
                                    'requester_id': user['id'],
                                    'notes': f'Verification requested by user {user.get("name", "")}'
                                })
                                st.success(f"✅ Request created!")
                                st.rerun()
                    with col5:
                        if st.button("🗑️ Remove", key=f"remove_{addr['address_id']}", type="secondary"):
                            db.unlink_address_from_user(user['id'], addr['address_id'])
                            st.success("✅ Address removed from your account")
                            st.rerun()
                    
                    # Share Dialog
                    if st.session_state.get(f"show_share_{addr['address_id']}", False):
                        st.markdown("#### 🔗 Share This Address")
                        with st.form(f"share_form_{addr['address_id']}"):
                            grantee_name = st.text_input("Recipient Name/Organization*")
                            grantee_type = st.selectbox("Recipient Type", 
                                                        ["AIU", "Bank", "Telecom", "Government", "E-commerce", "Other"])
                            purpose = st.text_area("Purpose of Access*")
                            scope = st.selectbox("Access Level", ["view", "verify", "full"])
                            expiry_days = st.slider("Access Valid For (Days)", 1, 365, 30)
                            
                            if st.form_submit_button("Generate Access Token"):
                                if grantee_name and purpose:
                                    consent_id, token = db.create_consent({
                                        'user_id': user['id'],
                                        'address_id': addr['address_id'],
                                        'grantee_name': grantee_name,
                                        'grantee_type': grantee_type,
                                        'purpose': purpose,
                                        'scope': scope,
                                        'expires_at': (datetime.now() + timedelta(days=expiry_days)).isoformat()
                                    })
                                    st.success(f"✅ Access granted! Consent ID: {consent_id}")
                                    st.code(token, language=None)
                                    st.info("📋 Share this token with the recipient. They can use it to access your address details.")
                                    st.session_state[f"show_share_{addr['address_id']}"] = False
                                else:
                                    st.error("❌ Please fill all required fields")
    
    # ========== TAB 2: ADD ADDRESS ==========
    with tab2:
        st.markdown("### ➕ Add New Address")
        
        add_method = st.radio("How would you like to add an address?", 
                             ["🔍 Search Existing", "📝 Create New"], 
                             horizontal=True)
        
        if add_method == "🔍 Search Existing":
            st.markdown("Search for an existing address by DIGIPIN or digital address")
            search_query = st.text_input("🔍 Enter DIGIPIN or Digital Address")
            
            if search_query:
                # Search in database
                results = db.search_addresses(search_query)
                
                if results:
                    st.success(f"Found {len(results)} address(es)")
                    for addr in results[:5]:
                        with st.container():
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""
                                **DIGIPIN:** `{addr.get('digipin', 'N/A')}`  
                                **Address:** {addr.get('descriptive_address', 'N/A')}
                                """)
                            with col2:
                                # Check if already linked
                                already_linked = any(ua['address_id'] == addr['id'] for ua in user_addresses)
                                if already_linked:
                                    st.info("✓ Already Added")
                                else:
                                    if st.button("➕ Add", key=f"add_{addr['id']}"):
                                        try:
                                            db.link_address_to_user(
                                                user['id'], 
                                                addr['id'], 
                                                label="Home",
                                                is_primary=len(user_addresses) == 0
                                            )
                                            st.success("✅ Address added to your account!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                            st.markdown("---")
                else:
                    st.warning("No addresses found. You can create a new one below.")
        
        else:  # Create New
            st.markdown("Create a new digital address")
            
            # Check if we need to show the "address exists" dialog
            if 'existing_address_conflict' in st.session_state and st.session_state.existing_address_conflict:
                conflict = st.session_state.existing_address_conflict
                existing = conflict['existing_address']
                
                st.warning(f"⚠️ Digital address `{conflict['digital_addr']}` already exists!")
                
                st.markdown(f"""
                <div style="background: rgba(255,152,0,0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ff9800; margin: 1rem 0;">
                    <strong>📍 Current Location:</strong><br>
                    {existing.get('descriptive_address', 'N/A')}<br>
                    <small>City: {existing.get('city', 'N/A')} | Confidence: {existing.get('confidence_score', 0):.0f}%</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**What would you like to do?**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Update Location", type="primary", use_container_width=True, 
                                help="I moved - update to new address"):
                        # Update the existing address
                        try:
                            address_id = existing['id']
                            db.update_address(address_id, {
                                'digipin': conflict['digipin'].upper().replace('-', ''),
                                'descriptive_address': conflict['descriptive'],
                                'latitude': conflict['lat'],
                                'longitude': conflict['lon'],
                                'city': conflict['city'],
                                'state': conflict['state'],
                                'pincode': conflict['pincode'],
                                'confidence_score': 50,  # Reset score for new location
                                'confidence_grade': 'C'
                            })
                            
                            # Check if already linked to user
                            already_linked = any(ua['address_id'] == address_id for ua in user_addresses)
                            if not already_linked:
                                db.link_address_to_user(user['id'], address_id, conflict['label'], conflict['is_primary'])
                            
                            # Create validation request
                            validation_id = db.create_validation({
                                'address_id': address_id,
                                'digital_address': conflict['digital_addr'],
                                'digipin': conflict['digipin'].upper().replace('-', ''),
                                'descriptive_address': conflict['descriptive'],
                                'validation_type': 'PHYSICAL',
                                'status': 'PENDING',
                                'priority': 'NORMAL',
                                'requester_id': user['id'],
                                'notes': f'Address location updated by {user.get("name", "user")}'
                            })
                            
                            st.session_state.existing_address_conflict = None
                            st.success(f"✅ Location updated! `{conflict['digital_addr']}` now points to new address.")
                            st.info(f"📋 Validation request **{validation_id}** created.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                with col2:
                    if st.button("➕ Create New", use_container_width=True,
                                help="Add as different address with new digital address"):
                        st.session_state.existing_address_conflict = None
                        st.session_state.prefill_address = {
                            'digipin': conflict['digipin'],
                            'descriptive': conflict['descriptive'],
                            'city': conflict['city'],
                            'state': conflict['state'],
                            'pincode': conflict['pincode'],
                            'label': conflict['label']
                        }
                        st.info("💡 Please enter a different digital address (e.g., `raj.office@aava.in`)")
                        st.rerun()
                
                with col3:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.existing_address_conflict = None
                        st.rerun()
                
                st.stop()
            
            # Check for prefilled data (from "Create New" option)
            prefill = st.session_state.get('prefill_address', {})
            
            with st.form("create_address_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    digipin = st.text_input("📍 DIGIPIN (10 characters)*", 
                                           value=prefill.get('digipin', ''),
                                           help="Enter the DIGIPIN code for your location")
                    digital_addr = st.text_input("📧 Digital Address", 
                                                 placeholder="username@provider.in",
                                                 help="Use different addresses for different locations (e.g., raj@aava.in, raj.office@aava.in)")
                    label = st.text_input("🏷️ Label", value=prefill.get('label', 'Home'), 
                                         help="e.g., Home, Office, Shop")
                
                with col2:
                    descriptive = st.text_area("📝 Descriptive Address*", 
                                               value=prefill.get('descriptive', ''),
                                               placeholder="House No, Street, Locality...")
                    col_city, col_state = st.columns(2)
                    with col_city:
                        city = st.text_input("🏙️ City", value=prefill.get('city', ''))
                    with col_state:
                        state = st.text_input("🗺️ State", value=prefill.get('state', ''))
                    pincode = st.text_input("📮 PIN Code", value=prefill.get('pincode', ''))
                
                # Clear prefill after form is shown
                if prefill:
                    st.session_state.prefill_address = {}
                
                is_primary = st.checkbox("Set as Primary Address", value=len(user_addresses) == 0)
                
                if st.form_submit_button("Create Address", use_container_width=True):
                    # Validate DIGIPIN
                    if not digipin:
                        st.error("❌ DIGIPIN is required")
                    elif not digipin_validator.validate(digipin):
                        st.error("❌ Invalid DIGIPIN format")
                    elif not descriptive:
                        st.error("❌ Descriptive address is required")
                    else:
                        # Decode DIGIPIN to get coordinates
                        decode_result = digipin_validator.decode(digipin)
                        
                        try:
                            # Check if digital address already exists
                            existing_address = None
                            if digital_addr:
                                existing_address = db.get_address_by_digital_address(digital_addr)
                            
                            if existing_address:
                                # Store conflict data and show dialog
                                st.session_state.existing_address_conflict = {
                                    'existing_address': existing_address,
                                    'digital_addr': digital_addr,
                                    'digipin': digipin,
                                    'descriptive': descriptive,
                                    'city': city,
                                    'state': state,
                                    'pincode': pincode,
                                    'label': label,
                                    'is_primary': is_primary,
                                    'lat': decode_result.center_lat,
                                    'lon': decode_result.center_lon
                                }
                                st.rerun()
                            else:
                                # Create NEW address
                                address_id = db.create_address({
                                    'digipin': digipin.upper().replace('-', ''),
                                    'digital_address': digital_addr if digital_addr else None,
                                    'descriptive_address': descriptive,
                                    'latitude': decode_result.center_lat,
                                    'longitude': decode_result.center_lon,
                                    'city': city,
                                    'state': state,
                                    'pincode': pincode,
                                    'confidence_score': 50,  # Initial score
                                    'confidence_grade': 'C'
                                })
                                
                                # Link to user
                                db.link_address_to_user(user['id'], address_id, label, is_primary)
                                
                                # Auto-create validation request for agent verification
                                validation_id = db.create_validation({
                                    'address_id': address_id,
                                    'digital_address': digital_addr if digital_addr else None,
                                    'digipin': digipin.upper().replace('-', ''),
                                    'descriptive_address': descriptive,
                                    'validation_type': 'PHYSICAL',
                                    'status': 'PENDING',
                                    'priority': 'NORMAL',
                                    'requester_id': user['id'],
                                    'notes': f'Auto-created for new address registration by {user.get("name", "user")}'
                                })
                                
                                st.success(f"✅ Address created! ID: {address_id}")
                                st.info(f"📋 Validation request **{validation_id}** auto-created. An agent will verify your address soon!")
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # ========== TAB 3: CONSENT MANAGEMENT ==========
    with tab3:
        st.markdown("### 🔐 Consent Management")
        st.markdown("Control who can access your address information")
        
        # Filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            show_all = st.checkbox("Show revoked consents", value=False)
        
        all_consents = db.get_user_consents(user['id'], include_revoked=show_all)
        
        if not all_consents:
            st.info("📭 No consents granted yet. Share an address to create a consent.")
        else:
            # Group by status
            active = [c for c in all_consents if not c.get('revoked') and 
                      (not c.get('expires_at') or c.get('expires_at') > datetime.now().isoformat())]
            expired = [c for c in all_consents if not c.get('revoked') and 
                       c.get('expires_at') and c.get('expires_at') <= datetime.now().isoformat()]
            revoked = [c for c in all_consents if c.get('revoked')]
            
            st.markdown(f"**Active:** {len(active)} | **Expired:** {len(expired)} | **Revoked:** {len(revoked)}")
            
            for consent in all_consents:
                is_revoked = consent.get('revoked')
                is_expired = consent.get('expires_at') and consent.get('expires_at') <= datetime.now().isoformat()
                
                status_class = "revoked" if is_revoked else ("expired" if is_expired else "active")
                status_icon = "🚫" if is_revoked else ("⏰" if is_expired else "✅")
                
                with st.expander(f"{status_icon} {consent.get('grantee_name')} - {consent.get('digipin', 'N/A')}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Recipient:** {consent.get('grantee_name')}  
                        **Type:** {consent.get('grantee_type', 'AIU')}  
                        **Purpose:** {consent.get('purpose', 'N/A')}  
                        **Scope:** {consent.get('scope', 'view')}  
                        **Address:** `{consent.get('digipin', 'N/A')}`
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Granted:** {consent.get('issued_at', 'N/A')[:10] if consent.get('issued_at') else 'N/A'}  
                        **Expires:** {consent.get('expires_at', 'Never')[:10] if consent.get('expires_at') else 'Never'}  
                        **Accesses:** {consent.get('access_count', 0)}  
                        **Last Access:** {consent.get('last_accessed', 'Never')[:16] if consent.get('last_accessed') else 'Never'}
                        """)
                    
                    if is_revoked:
                        st.error(f"🚫 Revoked on {consent.get('revoked_at', 'N/A')[:10] if consent.get('revoked_at') else 'N/A'}")
                        if consent.get('revocation_reason'):
                            st.markdown(f"**Reason:** {consent.get('revocation_reason')}")
                    elif is_expired:
                        st.warning("⏰ This consent has expired")
                    else:
                        # Show token (masked)
                        token = consent.get('access_token', '')
                        masked_token = token[:8] + "..." + token[-8:] if len(token) > 16 else token
                        st.code(f"Token: {masked_token}")
                        
                        # Revoke button
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            revoke_reason = st.text_input("Reason for revocation", 
                                                          key=f"reason_{consent['id']}")
                        with col2:
                            if st.button("🚫 Revoke Access", key=f"revoke_{consent['id']}", type="secondary"):
                                db.revoke_consent(consent['id'], revoke_reason)
                                st.success("✅ Consent revoked successfully")
                                st.rerun()
    
    # ========== TAB 4: ACCESS HISTORY ==========
    with tab4:
        st.markdown("### 📜 Access History")
        st.markdown("View who has accessed your address information")
        
        # Get all consents with access data
        all_consents = db.get_user_consents(user['id'], include_revoked=True)
        accessed_consents = [c for c in all_consents if c.get('access_count', 0) > 0]
        
        if not accessed_consents:
            st.info("📭 No access history yet")
        else:
            # Summary stats
            total_accesses = sum(c.get('access_count', 0) for c in all_consents)
            unique_grantees = len(set(c.get('grantee_name') for c in accessed_consents))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Accesses", total_accesses)
            with col2:
                st.metric("Unique Organizations", unique_grantees)
            with col3:
                st.metric("Active Shares", len([c for c in all_consents if not c.get('revoked')]))
            
            st.markdown("---")
            
            # Access log table
            import pandas as pd
            access_data = []
            for c in accessed_consents:
                access_data.append({
                    'Organization': c.get('grantee_name'),
                    'Type': c.get('grantee_type'),
                    'Address': c.get('digipin'),
                    'Purpose': c.get('purpose', '')[:30] + '...' if len(c.get('purpose', '')) > 30 else c.get('purpose', ''),
                    'Accesses': c.get('access_count', 0),
                    'Last Access': c.get('last_accessed', '')[:16] if c.get('last_accessed') else 'N/A',
                    'Status': '🚫 Revoked' if c.get('revoked') else '✅ Active'
                })
            
            if access_data:
                df = pd.DataFrame(access_data)
                st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================================
# MAIN APP LOGIC
# ============================================================================

if st.session_state.logged_in_user is None:
    show_login_register()
else:
    show_user_dashboard()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    <p>🔒 Your data is protected under India's Digital Personal Data Protection Act</p>
    <p>AAVA - Address Issuance Authority (AIA) • DHRUVA Initiative</p>
</div>
""", unsafe_allow_html=True)
