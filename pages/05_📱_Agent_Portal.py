# pages/3_📱_Agent_Portal.py
# AAVA - Agent Portal Page
# Field agent verification portal

import streamlit as st
import sys
import os
from datetime import datetime
import json
import base64
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.digipin import DIGIPINValidator

st.set_page_config(
    page_title="Agent Portal - AAVA",
    page_icon="📱",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()

# Custom CSS
st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; white-space: nowrap !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; overflow: visible !important; text-overflow: clip !important; }
    
    .agent-header {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #2196F3;
    }
    .task-card.urgent {
        border-left-color: #f44336;
    }
    .task-card.high {
        border-left-color: #ff9800;
    }
    .evidence-upload {
        background: #f5f5f5;
        padding: 1.5rem;
        border-radius: 8px;
        border: 2px dashed #ccc;
        text-align: center;
    }
    .status-active {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .status-offline {
        background: #ffebee;
        color: #c62828;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state for agent
if 'logged_in_agent' not in st.session_state:
    st.session_state.logged_in_agent = None

if 'current_task' not in st.session_state:
    st.session_state.current_task = None


# =============================================================================
# LOGIN SECTION
# =============================================================================

def agent_login_form():
    """Display agent login form."""
    st.markdown("""
    <div class="agent-header">
        <h1 style="margin: 0;">📱 Agent Portal</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Field Verification Agent Login</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Agent Login")
        
        with st.form("agent_login"):
            agent_id = st.text_input(
                "Agent ID",
                placeholder="AGT-XXXXXXXX"
            )
            
            email = st.text_input(
                "Email",
                placeholder="agent@aava.in"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                submit = st.form_submit_button("🔑 Login", use_container_width=True)
            
            if submit:
                if agent_id and email:
                    agent = db.get_agent_by_email(email)
                    
                    if agent and agent.get('id') == agent_id:
                        st.session_state.logged_in_agent = agent
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("Please enter Agent ID and Email")
        
        st.divider()
        
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>🔐 Secure agent authentication</p>
            <p>Contact admin if you forgot your credentials</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# AGENT DASHBOARD
# =============================================================================

def agent_dashboard():
    """Display agent dashboard with tasks."""
    agent = st.session_state.logged_in_agent
    
    # Header with agent info and logout button
    col_header, col_logout = st.columns([5, 1])
    with col_header:
        st.markdown(f"""
        <div class="agent-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1 style="margin: 0;">📱 Agent Portal</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                        Welcome, {agent.get('name', 'Agent')}
                    </p>
                </div>
                <div style="text-align: right;">
                    <span class="status-active">🟢 Active</span>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                        ID: {agent.get('id', 'N/A')}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, key="agent_logout_main"):
            st.session_state.logged_in_agent = None
            st.session_state.current_task = None
            st.rerun()
    
    # Sidebar for agent info
    with st.sidebar:
        st.markdown("### 👤 Agent Profile")
        st.markdown(f"""
        **Name:** {agent.get('name', 'N/A')}  
        **ID:** {agent.get('id', 'N/A')}  
        **Email:** {agent.get('email', 'N/A')}  
        **Performance:** {agent.get('performance_score', 0) * 100:.0f}%
        """)
    
    # Check if we should show alert for pending verification
    if st.session_state.get('active_tab') == 'submit' and st.session_state.current_task:
        st.success("✅ **Task started!** Go to '✅ Submit Verification' tab to complete the verification.")
        st.session_state.active_tab = None  # Clear after showing
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Assigned Tasks", "✅ Submit Verification", "📊 My Stats"])
    
    # -------------------------------------------------------------------------
    # TAB 1: ASSIGNED TASKS
    # -------------------------------------------------------------------------
    
    with tab1:
        st.markdown("### 📋 Your Assigned Tasks")
        
        # Get tasks for this agent
        tasks = db.get_validations_by_agent(agent.get('id'))
        
        # Filter to only pending/in-progress
        active_tasks = [
            t for t in tasks 
            if t.get('status') in ['PENDING', 'IN_PROGRESS']
        ]
        
        # Also get UNASSIGNED pending validations (available to claim)
        all_validations = db.get_all_validations()
        unassigned_tasks = [
            v for v in all_validations 
            if v.get('status') == 'PENDING' and not v.get('assigned_agent_id')
        ]
        
        # Show unassigned tasks first (available to claim)
        if unassigned_tasks:
            st.markdown("#### 🆕 Available Tasks (Claim to Start)")
            st.info(f"📢 **{len(unassigned_tasks)} validation request(s)** waiting to be claimed!")
            
            for task in unassigned_tasks[:5]:  # Show max 5
                priority = task.get('priority', 'NORMAL')
                priority_badge = {
                    'LOW': '🟢 Low',
                    'NORMAL': '🔵 Normal', 
                    'HIGH': '🟠 High',
                    'URGENT': '🔴 Urgent'
                }.get(priority, '🔵 Normal')
                
                with st.container():
                    col_info, col_btn = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"""
                        **{task.get('id')}** | {priority_badge}  
                        📍 {task.get('digipin', 'N/A')} | {task.get('descriptive_address', 'No address')[:50]}...
                        """)
                    with col_btn:
                        if st.button("✋ Claim", key=f"claim_{task.get('id')}", type="primary"):
                            # Assign to this agent
                            db.update_validation(task.get('id'), {
                                'assigned_agent_id': agent.get('id'),
                                'status': 'IN_PROGRESS'
                            })
                            st.success(f"✅ Task {task.get('id')} claimed!")
                            st.rerun()
            
            st.divider()
        
        if not active_tasks and not unassigned_tasks:
            # No tasks available - show message
            st.info("📋 No tasks available. New validation requests will appear here when users request verification.")
        
        # Show assigned/claimed tasks
        if active_tasks:
            st.markdown("#### ✅ Your Active Tasks")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                for task in active_tasks:
                    priority = task.get('priority', 'NORMAL')
                    card_class = 'task-card'
                    if priority == 'URGENT':
                        card_class += ' urgent'
                    elif priority == 'HIGH':
                        card_class += ' high'
                    
                    priority_badge = {
                        'LOW': '🟢 Low',
                        'NORMAL': '🔵 Normal',
                        'HIGH': '🟠 High',
                        'URGENT': '🔴 Urgent'
                    }.get(priority, '🔵 Normal')
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0;">{task.get('id', 'N/A')}</h4>
                                <p style="margin: 0.25rem 0; color: #666;">
                                    📍 {validator._format_digipin(task.get('digipin', ''))}
                                </p>
                            </div>
                            <span style="font-size: 0.9rem;">{priority_badge}</span>
                        </div>
                        <p style="margin: 0.5rem 0; font-size: 0.9rem;">
                            {task.get('descriptive_address', 'No address')}
                        </p>
                        <div style="display: flex; justify-content: space-between; 
                                    margin-top: 0.5rem; font-size: 0.8rem; color: #999;">
                            <span>Type: {task.get('validation_type', 'PHYSICAL')}</span>
                            <span>Status: {task.get('status', 'PENDING')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"📍 Start Verification", key=f"start_{task.get('id')}"):
                        st.session_state.current_task = task
                        st.session_state.active_tab = "submit"  # Switch to submit tab
                        # Update status to IN_PROGRESS
                        db.update_validation(task.get('id'), {'status': 'IN_PROGRESS'})
                        st.rerun()
            
            with col2:
                st.markdown("#### 📊 Task Summary")
                
                pending = len([t for t in active_tasks if t.get('status') == 'PENDING'])
                in_progress = len([t for t in active_tasks if t.get('status') == 'IN_PROGRESS'])
                
                st.metric("Pending", pending)
                st.metric("In Progress", in_progress)
                
                st.divider()
                
                st.markdown("#### 🗺️ Location Overview")
                
                # Create map with all task locations
                import plotly.graph_objects as go
                
                lats = []
                lons = []
                texts = []
                
                for task in active_tasks:
                    digipin = task.get('digipin', '')
                    if digipin:
                        result = validator.decode(digipin)
                        if result.valid:
                            lats.append(result.center_lat)
                            lons.append(result.center_lon)
                            texts.append(f"{task.get('id')}<br>{result.formatted}")
                
                if lats:
                    fig = go.Figure(go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode='markers',
                        marker=go.scattermapbox.Marker(size=12, color='red'),
                        text=texts,
                        hoverinfo='text'
                    ))
                    
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            center=dict(lat=sum(lats)/len(lats), lon=sum(lons)/len(lons)),
                            zoom=10
                        ),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------------------------------------------------
    # TAB 2: SUBMIT VERIFICATION
    # -------------------------------------------------------------------------
    
    with tab2:
        st.markdown("### ✅ Submit Verification Report")
        
        if st.session_state.current_task:
            task = st.session_state.current_task
            
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <h4 style="margin: 0;">Current Task: {task.get('id')}</h4>
                <p style="margin: 0.5rem 0 0 0;">
                    📍 {validator._format_digipin(task.get('digipin', ''))}
                </p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.9rem; color: #666;">
                    {task.get('descriptive_address', 'No address')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Decode DIGIPIN for map
            digipin = task.get('digipin', '')
            if digipin:
                result = validator.decode(digipin)
                if result.valid:
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(go.Scattermapbox(
                        lat=[result.center_lat],
                        lon=[result.center_lon],
                        mode='markers',
                        marker=go.scattermapbox.Marker(size=16, color='red'),
                        text=[f"Target: {result.formatted}"],
                        hoverinfo='text'
                    ))
                    
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            center=dict(lat=result.center_lat, lon=result.center_lon),
                            zoom=16
                        ),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Verification Form
            with st.form("verification_form"):
                st.markdown("#### 📸 Evidence Collection")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Photo upload
                    photos = st.file_uploader(
                        "Upload Photos (max 5)",
                        type=['jpg', 'jpeg', 'png'],
                        accept_multiple_files=True,
                        help="Take clear photos of the location"
                    )
                    
                    if photos:
                        st.markdown(f"📷 {len(photos)} photo(s) selected")
                        for photo in photos[:5]:
                            st.image(photo, width=100)
                
                with col2:
                    # GPS coordinates
                    st.markdown("##### 📍 GPS Coordinates")
                    
                    gps_lat = st.number_input(
                        "Latitude",
                        min_value=2.5,
                        max_value=38.5,
                        value=result.center_lat if digipin and result.valid else 28.6139,
                        format="%.6f"
                    )
                    
                    gps_lon = st.number_input(
                        "Longitude",
                        min_value=63.5,
                        max_value=99.5,
                        value=result.center_lon if digipin and result.valid else 77.2090,
                        format="%.6f"
                    )
                    
                    gps_accuracy = st.slider(
                        "GPS Accuracy (meters)",
                        min_value=1,
                        max_value=50,
                        value=5
                    )
                
                st.divider()
                
                st.markdown("#### ✅ Verification Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    verified = st.radio(
                        "Address Verified?",
                        options=["Yes - Address exists and is correct",
                                "Partial - Address exists but needs correction",
                                "No - Address not found or incorrect"],
                        index=0
                    )
                    
                    evidence_type = st.multiselect(
                        "Evidence Collected",
                        options=["Photo", "Video", "Signature", "ID Verification", "Utility Bill"],
                        default=["Photo"]
                    )
                
                with col2:
                    quality_score = st.slider(
                        "Verification Quality (1-10)",
                        min_value=1,
                        max_value=10,
                        value=8,
                        help="Rate the quality of evidence collected"
                    )
                    
                    occupant_present = st.checkbox("Occupant was present", value=True)
                    building_accessible = st.checkbox("Building/location accessible", value=True)
                
                notes = st.text_area(
                    "Verification Notes",
                    placeholder="Enter any observations, landmarks, or additional details...",
                    height=100
                )
                
                # Submit buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    submit = st.form_submit_button("✅ Submit Verification", type="primary")
                
                with col2:
                    save_draft = st.form_submit_button("💾 Save Draft")
                
                with col3:
                    cancel = st.form_submit_button("❌ Cancel")
                
                if submit:
                    # Determine if verified
                    is_verified = verified.startswith("Yes")
                    
                    # Calculate quality score (0-1)
                    calculated_quality = quality_score / 10
                    
                    # Store photos (in real app, would upload to storage)
                    photo_list = [f"photo_{i+1}.jpg" for i in range(len(photos or []))]
                    
                    try:
                        # Create verification record
                        ver_id = db.create_verification({
                            'validation_id': task.get('id'),
                            'agent_id': agent.get('id'),
                            'verified': 1 if is_verified else 0,
                            'quality_score': calculated_quality,
                            'evidence_type': ','.join(evidence_type),
                            'photos': photo_list,
                            'gps_latitude': gps_lat,
                            'gps_longitude': gps_lon,
                            'gps_accuracy': gps_accuracy,
                            'notes': notes
                        })
                        
                        # Update validation status
                        db.update_validation(task.get('id'), {
                            'status': 'COMPLETED',
                            'completed_at': datetime.now().isoformat()
                        })
                        
                        # Update agent stats
                        current_stats = db.get_agent_stats(agent.get('id'))
                        db.update_agent(agent.get('id'), {
                            'total_verifications': current_stats.get('total_verifications', 0) + 1,
                            'successful_verifications': current_stats.get('successful_verifications', 0) + (1 if is_verified else 0),
                            'last_active': datetime.now().isoformat()
                        })
                        
                        # ============================================================
                        # UPDATE CONFIDENCE SCORE AFTER VERIFICATION
                        # ============================================================
                        address_id = task.get('address_id')
                        if address_id:
                            try:
                                # Get the address
                                address = db.get_address(address_id)
                                if address:
                                    current_score = float(address.get('confidence_score', 50))
                                    
                                    if is_verified:
                                        # Physical verification boost formula:
                                        # Base boost = 30% (for getting verified)
                                        # Quality bonus = quality_score * 20% (0-20% extra)
                                        # Total possible boost: 30% + 20% = 50%
                                        # So 50% + 50% = 100% max with quality=100%
                                        base_boost = 30
                                        quality_bonus = 20 * calculated_quality
                                        verification_boost = base_boost + quality_bonus
                                        new_score = min(100, current_score + verification_boost)
                                        new_grade = 'A+' if new_score >= 90 else 'A' if new_score >= 80 else 'B' if new_score >= 70 else 'C' if new_score >= 60 else 'D' if new_score >= 50 else 'F'
                                    else:
                                        # Failed verification reduces score
                                        new_score = max(0, current_score - 10)
                                        new_grade = 'A+' if new_score >= 90 else 'A' if new_score >= 80 else 'B' if new_score >= 70 else 'C' if new_score >= 60 else 'D' if new_score >= 50 else 'F'
                                    
                                    # Update address with new confidence score
                                    db.update_address(address_id, {
                                        'confidence_score': new_score,
                                        'confidence_grade': new_grade
                                    })
                                    
                            except Exception as score_error:
                                # Log but don't fail the verification
                                print(f"Warning: Could not update confidence score: {score_error}")
                        
                        # Log audit
                        db.log_audit({
                            'actor': agent.get('id'),
                            'action': 'verification.submitted',
                            'resource_type': 'verification',
                            'resource_id': ver_id,
                            'details': {
                                'validation_id': task.get('id'),
                                'verified': is_verified,
                                'quality': calculated_quality
                            }
                        })
                        
                        st.success(f"""
                        ✅ Verification submitted successfully!
                        
                        **Verification ID:** {ver_id}  
                        **Status:** {'Verified' if is_verified else 'Not Verified'}  
                        **Quality Score:** {calculated_quality:.0%}
                        """)
                        
                        # Clear current task
                        st.session_state.current_task = None
                        
                    except Exception as e:
                        st.error(f"❌ Error submitting verification: {str(e)}")
                
                if cancel:
                    st.session_state.current_task = None
                    st.rerun()
        
        else:
            st.info("📋 No task selected. Please select a task from the Assigned Tasks tab.")
            
            # Quick task selection
            active_tasks = [
                t for t in db.get_validations_by_agent(agent.get('id'))
                if t.get('status') in ['PENDING', 'IN_PROGRESS']
            ]
            
            if active_tasks:
                st.markdown("#### Quick Select")
                for task in active_tasks[:3]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📍 {task.get('id')} - {task.get('digipin', 'N/A')}")
                    with col2:
                        if st.button("Select", key=f"quick_{task.get('id')}"):
                            st.session_state.current_task = task
                            db.update_validation(task.get('id'), {'status': 'IN_PROGRESS'})
                            st.rerun()
    
    # -------------------------------------------------------------------------
    # TAB 3: MY STATS
    # -------------------------------------------------------------------------
    
    with tab3:
        st.markdown("### 📊 My Performance Statistics")
        
        stats = db.get_agent_stats(agent.get('id'))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Verifications",
                stats.get('total_verifications', 0)
            )
        
        with col2:
            st.metric(
                "Successful",
                stats.get('successful_verifications', 0)
            )
        
        with col3:
            success_rate = stats.get('success_rate', 0) * 100
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%"
            )
        
        with col4:
            perf = agent.get('performance_score', 0) * 100
            st.metric(
                "Performance Score",
                f"{perf:.1f}%"
            )
        
        st.divider()
        
        # Recent verifications
        st.markdown("#### 📋 Recent Verifications")
        
        recent = db.get_verifications_by_agent(agent.get('id'), limit=10)
        
        if recent:
            for ver in recent:
                status_icon = "✅" if ver.get('verified') else "❌"
                quality = ver.get('quality_score', 0) * 100
                
                st.markdown(f"""
                <div style="background: white; padding: 0.75rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between;">
                        <span>{status_icon} {ver.get('id', 'N/A')}</span>
                        <span style="color: #666;">Quality: {quality:.0f}%</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #999; margin-top: 0.25rem;">
                        {ver.get('timestamp', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No verifications yet. Complete your first task!")


# =============================================================================
# MAIN
# =============================================================================

if st.session_state.logged_in_agent:
    agent_dashboard()
else:
    agent_login_form()
