# pages/07_📋_Address_Registry.py
# AAVA - Address Registry (Combined AIP + AIU)
# Digital Address Registry, Verification Tracking & Third-Party Access

import streamlit as st
import sys
import os
import pandas as pd
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager

st.set_page_config(
    page_title="Address Registry - AAVA",
    page_icon="📋",
    layout="wide"
)

# Initialize
db = DatabaseManager()
db.initialize()

# CSS
st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; }
    [data-testid="stSidebar"] > div:first-child { width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; white-space: nowrap !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; overflow: visible !important; text-overflow: clip !important; }
    .registry-stat {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .address-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .verified { border-left-color: #28a745; }
    .pending { border-left-color: #ffc107; }
    .unverified { border-left-color: #dc3545; }
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
            padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <h1 style="margin: 0;">📋 Address Registry</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        AIP Registry • AIU Token Access • Verification Tracking • Address Data Management
    </p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
### Address Information Provider (AIP) & User (AIU) Portal

This unified registry provides:
- 📍 **AIP Functions**: Core address data, verification details, and registry management
- 🔗 **AIU Functions**: Third-party token-based address access for authorized organizations
- ✅ Verification tracking and AIA (Agent) assignments
- 🔒 Secure consent-based data sharing
""")

st.markdown("---")

# Get all addresses
all_addresses = db.get_all_addresses(limit=1000)
all_validations = db.get_all_validations()
all_agents = db.get_all_agents()

# Stats Row
st.markdown("## 📊 Registry Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

# Calculate stats
verified_count = len([a for a in all_addresses if a.get('confidence_score', 0) >= 70])
pending_count = len([a for a in all_addresses if 30 <= a.get('confidence_score', 0) < 70])
unverified_count = len([a for a in all_addresses if a.get('confidence_score', 0) < 30])
total_validations = len(all_validations)
active_agents = len([a for a in all_agents if a.get('active')])

with col1:
    st.markdown(f"""
    <div class="registry-stat">
        <h2 style="margin: 0;">{len(all_addresses)}</h2>
        <p style="margin: 0; opacity: 0.9;">Total Addresses</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="registry-stat" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
        <h2 style="margin: 0;">{verified_count}</h2>
        <p style="margin: 0; opacity: 0.9;">Verified (A/B)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="registry-stat" style="background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);">
        <h2 style="margin: 0;">{pending_count}</h2>
        <p style="margin: 0; opacity: 0.9;">Pending (C/D)</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="registry-stat" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
        <h2 style="margin: 0;">{unverified_count}</h2>
        <p style="margin: 0; opacity: 0.9;">Unverified (F)</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="registry-stat" style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);">
        <h2 style="margin: 0;">{active_agents}</h2>
        <p style="margin: 0; opacity: 0.9;">Active AIAs</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Address Registry", 
    "🔗 AIU Token Access",
    "✅ Verification Status",
    "👤 AIA Assignments",
    "📈 Registry Analytics"
])

# ========== TAB 1: ADDRESS REGISTRY ==========
with tab1:
    st.markdown("### 📋 Digital Address Registry")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_grade = st.selectbox("Filter by Grade", ["All", "A", "B", "C", "D", "F"])
    with col2:
        filter_state = st.selectbox("Filter by State", ["All"] + list(set(a.get('state', '') for a in all_addresses if a.get('state'))))
    with col3:
        search_query = st.text_input("🔍 Search (DIGIPIN/Address)")
    
    # Apply filters
    filtered_addresses = all_addresses
    if filter_grade != "All":
        filtered_addresses = [a for a in filtered_addresses if a.get('confidence_grade') == filter_grade]
    if filter_state != "All":
        filtered_addresses = [a for a in filtered_addresses if a.get('state') == filter_state]
    if search_query:
        search_lower = search_query.lower()
        filtered_addresses = [a for a in filtered_addresses if 
                             search_lower in (a.get('digipin', '') or '').lower() or
                             search_lower in (a.get('descriptive_address', '') or '').lower() or
                             search_lower in (a.get('digital_address', '') or '').lower()]
    
    st.markdown(f"**Showing {len(filtered_addresses)} addresses**")
    
    if filtered_addresses:
        # Convert to DataFrame for display
        df_data = []
        for addr in filtered_addresses:
            digipin = addr.get('digipin', 'N/A')
            formatted_digipin = f"{digipin[:3]}-{digipin[3:6]}-{digipin[6:]}" if len(digipin or '') == 10 else digipin
            df_data.append({
                'ID': addr.get('id', ''),
                'DIGIPIN': formatted_digipin,
                'Digital Address': addr.get('digital_address', 'N/A'),
                'City': addr.get('city', 'N/A'),
                'State': addr.get('state', 'N/A'),
                'PIN': addr.get('pincode', 'N/A'),
                'Score': f"{addr.get('confidence_score', 0):.0f}%",
                'Grade': addr.get('confidence_grade', 'F'),
                'Created': addr.get('created_at', '')[:10] if addr.get('created_at') else 'N/A'
            })
        
        df = pd.DataFrame(df_data)
        
        # Color-code the grade column
        def highlight_grade(val):
            colors = {'A': '#d4edda', 'B': '#d4edda', 'C': '#fff3cd', 'D': '#ffe5d0', 'F': '#f8d7da'}
            return f'background-color: {colors.get(val, "white")}'
        
        st.dataframe(
            df.style.applymap(highlight_grade, subset=['Grade']),
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export Registry (CSV)",
            data=csv,
            file_name=f"aip_registry_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No addresses found matching the filters")

# ========== TAB 2: AIU TOKEN ACCESS ==========
with tab2:
    st.markdown("### 🔗 AIU Token Access Portal")
    st.markdown("""
    **Address Information Users (AIUs)** are organizations that need to access verified address 
    information with user consent. Use the token provided by the user to retrieve their address details.
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        access_token = st.text_input(
            "Access Token",
            placeholder="Paste the access token provided by the user...",
            help="This token was generated when the user shared their address with your organization",
            key="aiu_token"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        verify_btn = st.button("🔍 Verify & Retrieve", use_container_width=True, type="primary")
    
    if verify_btn and access_token:
        with st.spinner("Verifying token and retrieving address..."):
            consent = db.get_consent_by_token(access_token.strip())
            
            if consent:
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
                    
                    digipin = consent.get('digipin', 'N/A')
                    formatted_digipin = f"{digipin[:3]}-{digipin[3:6]}-{digipin[6:]}" if len(digipin) == 10 else digipin
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                        <span style="color: #1565c0; font-weight: 500;">DIGIPIN</span><br>
                        <span style="font-size: 1.5rem; font-weight: bold; font-family: monospace;">{formatted_digipin}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if consent.get('digital_address'):
                        st.markdown(f"**Digital Address:** {consent.get('digital_address')}")
                    
                    st.markdown(f"**Descriptive Address:**")
                    st.info(consent.get('descriptive_address', 'N/A'))
                    
                    st.markdown(f"**City:** {consent.get('city', 'N/A')}")
                    st.markdown(f"**State:** {consent.get('state', 'N/A')}")
                    st.markdown(f"**PIN Code:** {consent.get('pincode', 'N/A')}")
                
                with col2:
                    st.markdown("#### Location & Verification")
                    
                    lat = consent.get('latitude')
                    lon = consent.get('longitude')
                    
                    if lat and lon:
                        st.markdown(f"**Coordinates:** {lat:.6f}, {lon:.6f}")
                        map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                        st.map(map_data, zoom=15)
                    
                    score = consent.get('confidence_score', 0)
                    grade = consent.get('confidence_grade', 'F')
                    grade_color = {'A': '#28a745', 'B': '#5cb85c', 'C': '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'}.get(grade, '#6c757d')
                    
                    st.markdown(f"""
                    <div style="background: {grade_color}20; padding: 1rem; border-radius: 8px; 
                                border: 2px solid {grade_color}; text-align: center; margin-top: 1rem;">
                        <span style="color: #666;">Confidence Score</span><br>
                        <span style="font-size: 2rem; font-weight: bold; color: {grade_color};">{grade}</span><br>
                        <span style="font-size: 1.2rem; font-weight: 600;">{score:.0f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export
                st.markdown("---")
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
                    "retrieved_at": datetime.now().isoformat()
                }
                
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"address_{consent.get('digipin', 'data')}.json",
                    mime="application/json"
                )
                
            else:
                st.markdown("""
                <div class="error-card">
                    <h3 style="color: #dc3545; margin: 0;">❌ Token Invalid or Expired</h3>
                    <p style="margin: 0.5rem 0 0 0; color: #721c24;">
                        The access token could not be verified.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **Possible Reasons:**
                - Token expired or revoked
                - Invalid or corrupted token
                - Token does not exist
                """)
    
    elif verify_btn and not access_token:
        st.warning("⚠️ Please enter an access token")

# ========== TAB 3: VERIFICATION STATUS ==========
with tab3:
    st.markdown("### ✅ Verification Status Tracking")
    
    # Get validations with details
    if all_validations:
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        completed = len([v for v in all_validations if v.get('status') == 'COMPLETED'])
        in_progress = len([v for v in all_validations if v.get('status') == 'IN_PROGRESS'])
        pending = len([v for v in all_validations if v.get('status') == 'PENDING'])
        failed = len([v for v in all_validations if v.get('status') == 'FAILED'])
        
        with col1:
            st.metric("Completed", completed, delta=None)
        with col2:
            st.metric("In Progress", in_progress)
        with col3:
            st.metric("Pending", pending)
        with col4:
            st.metric("Failed", failed)
        
        st.markdown("---")
        
        # Validation table
        val_data = []
        for val in all_validations[:50]:  # Show latest 50
            val_data.append({
                'Validation ID': val.get('id', ''),
                'DIGIPIN': val.get('digipin', 'N/A'),
                'Type': val.get('validation_type', 'N/A'),
                'Status': val.get('status', 'N/A'),
                'Priority': val.get('priority', 'NORMAL'),
                'Agent': val.get('assigned_agent_id', 'Unassigned') or 'Unassigned',
                'Created': val.get('created_at', '')[:10] if val.get('created_at') else 'N/A'
            })
        
        df_val = pd.DataFrame(val_data)
        
        def highlight_status(val):
            colors = {
                'COMPLETED': '#d4edda', 
                'IN_PROGRESS': '#cce5ff', 
                'PENDING': '#fff3cd', 
                'FAILED': '#f8d7da'
            }
            return f'background-color: {colors.get(val, "white")}'
        
        st.dataframe(
            df_val.style.applymap(highlight_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📭 No validations recorded yet")

# ========== TAB 4: AIA ASSIGNMENTS ==========
with tab4:
    st.markdown("### 👤 AIA (Agent) - Address Assignments")
    st.markdown("Track which Address Information Agent (AIA) supports each Digital Address")
    
    if all_agents:
        for agent in all_agents:
            agent_id = agent.get('id')
            agent_name = agent.get('name', 'Unknown')
            agent_active = "🟢 Active" if agent.get('active') else "🔴 Inactive"
            
            # Get validations assigned to this agent
            agent_validations = [v for v in all_validations if v.get('assigned_agent_id') == agent_id]
            completed_count = len([v for v in agent_validations if v.get('status') == 'COMPLETED'])
            
            with st.expander(f"👤 {agent_name} ({agent_id}) - {agent_active} | {len(agent_validations)} assignments"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    **Email:** {agent.get('email', 'N/A')}  
                    **Phone:** {agent.get('phone', 'N/A')}  
                    **Certification:** {agent.get('certification_date', 'N/A')} to {agent.get('certification_expiry', 'N/A')}  
                    **Performance Score:** {agent.get('performance_score', 0)*100:.0f}%
                    """)
                
                with col2:
                    st.metric("Total Assignments", len(agent_validations))
                    st.metric("Completed", completed_count)
                    if agent_validations:
                        success_rate = completed_count / len(agent_validations) * 100
                        st.metric("Success Rate", f"{success_rate:.0f}%")
                
                # Show assigned addresses
                if agent_validations:
                    st.markdown("**Assigned Addresses:**")
                    for val in agent_validations[:5]:
                        status_icon = {"COMPLETED": "✅", "IN_PROGRESS": "🔄", "PENDING": "⏳", "FAILED": "❌"}.get(val.get('status'), "❓")
                        st.markdown(f"- {status_icon} `{val.get('digipin', 'N/A')}` - {val.get('status')}")
                    if len(agent_validations) > 5:
                        st.markdown(f"_...and {len(agent_validations) - 5} more_")
    else:
        st.info("📭 No agents registered yet")

# ========== TAB 5: REGISTRY ANALYTICS ==========
with tab5:
    st.markdown("### 📈 Registry Analytics")
    
    if all_addresses:
        col1, col2 = st.columns(2)
        
        with col1:
            # Grade Distribution
            st.markdown("#### Grade Distribution")
            grade_counts = {}
            for addr in all_addresses:
                grade = addr.get('confidence_grade', 'F')
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            if grade_counts:
                import plotly.express as px
                fig = px.pie(
                    values=list(grade_counts.values()),
                    names=list(grade_counts.keys()),
                    color=list(grade_counts.keys()),
                    color_discrete_map={'A': '#28a745', 'B': '#5cb85c', 'C': '#ffc107', 'D': '#fd7e14', 'F': '#dc3545'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # State Distribution
            st.markdown("#### Addresses by State")
            state_counts = {}
            for addr in all_addresses:
                state = addr.get('state', 'Unknown') or 'Unknown'
                state_counts[state] = state_counts.get(state, 0) + 1
            
            if state_counts:
                # Sort and take top 10
                sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                fig = px.bar(
                    x=[s[0] for s in sorted_states],
                    y=[s[1] for s in sorted_states],
                    labels={'x': 'State', 'y': 'Count'}
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Score Distribution
        st.markdown("#### Confidence Score Distribution")
        scores = [addr.get('confidence_score', 0) for addr in all_addresses]
        if scores:
            fig = px.histogram(scores, nbins=20, labels={'value': 'Confidence Score', 'count': 'Number of Addresses'})
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Registry Health
        st.markdown("#### Registry Health Metrics")
        col1, col2, col3 = st.columns(3)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        high_quality = len([s for s in scores if s >= 70]) / len(scores) * 100 if scores else 0
        
        with col1:
            st.metric("Average Confidence Score", f"{avg_score:.1f}%")
        with col2:
            st.metric("High Quality Rate (≥70%)", f"{high_quality:.1f}%")
        with col3:
            coverage = len([a for a in all_addresses if a.get('latitude') and a.get('longitude')]) / len(all_addresses) * 100 if all_addresses else 0
            st.metric("Geo-coverage", f"{coverage:.1f}%")
    else:
        st.info("📭 No data available for analytics")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    <p>📚 AIP - Address Information Provider</p>
    <p>Maintaining secure and accurate digital address registry • DHRUVA Initiative</p>
</div>
""", unsafe_allow_html=True)
