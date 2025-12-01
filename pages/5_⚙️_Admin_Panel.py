# pages/5_⚙️_Admin_Panel.py
# AAVA - Admin Panel
# System administration and management

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta
import random
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.digipin import DIGIPINValidator
from utils.confidence_score import SampleDataGenerator, get_grade

st.set_page_config(
    page_title="Admin Panel - AAVA",
    page_icon="⚙️",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()

# Custom CSS
st.markdown("""
<style>
    /* Sidebar Navigation */
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; }
    
    .admin-header {
        background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="admin-header">
    <h1 style="margin: 0;">⚙️ Admin Panel</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">System Administration & Management</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📋 Validations",
    "👥 Agents",
    "🎲 Sample Data",
    "📝 Audit Logs"
])

# =============================================================================
# TAB 1: DASHBOARD
# =============================================================================

with tab1:
    st.markdown("### 📊 System Dashboard")
    
    # Get stats
    try:
        stats = db.get_dashboard_stats()
        
        # Top metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_addresses', 0):,}</div>
                <div class="stat-label">Total Addresses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_validations', 0):,}</div>
                <div class="stat-label">Total Validations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats.get('pending_validations', 0):,}</div>
                <div class="stat-label">Pending</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{stats.get('active_agents', 0):,}</div>
                <div class="stat-label">Active Agents</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            delivery_rate = stats.get('delivery_success_rate', 0)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{delivery_rate:.1f}%</div>
                <div class="stat-label">Delivery Success</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Validation Status")
            
            val_stats = db.get_validation_stats()
            status_data = val_stats.get('by_status', {})
            
            if status_data:
                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800', '#F44336', '#9E9E9E']
                )
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No validation data")
        
        with col2:
            st.markdown("#### Validation Types")
            
            type_data = val_stats.get('by_type', {})
            
            if type_data:
                fig = px.bar(
                    x=list(type_data.keys()),
                    y=list(type_data.values()),
                    color_discrete_sequence=['#2196F3']
                )
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No validation data")
        
        # System health
        st.divider()
        st.markdown("#### 🔧 System Health")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 8px;">
                <h4 style="margin: 0; color: #2e7d32;">🟢 Database</h4>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Connected & Healthy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 8px;">
                <h4 style="margin: 0; color: #2e7d32;">🟢 DIGIPIN Service</h4>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Operational</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: #e8f5e9; padding: 1rem; border-radius: 8px;">
                <h4 style="margin: 0; color: #2e7d32;">🟢 Scoring Engine</h4>
                <p style="margin: 0.5rem 0 0 0; color: #666;">Active</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")


# =============================================================================
# TAB 2: VALIDATIONS MANAGEMENT
# =============================================================================

with tab2:
    st.markdown("### 📋 Validation Management")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            options=["All", "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"],
            key="admin_status"
        )
    
    with col2:
        type_filter = st.selectbox(
            "Type",
            options=["All", "PHYSICAL", "DIGITAL", "HYBRID"],
            key="admin_type"
        )
    
    with col3:
        priority_filter = st.selectbox(
            "Priority",
            options=["All", "URGENT", "HIGH", "NORMAL", "LOW"],
            key="admin_priority"
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Refresh", key="refresh_val")
    
    # Get validations
    validations = db.get_all_validations(limit=200)
    
    # Apply filters
    if status_filter != "All":
        validations = [v for v in validations if v.get('status') == status_filter]
    if type_filter != "All":
        validations = [v for v in validations if v.get('validation_type') == type_filter]
    if priority_filter != "All":
        validations = [v for v in validations if v.get('priority') == priority_filter]
    
    if validations:
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'ID': v.get('id', ''),
                'DIGIPIN': validator._format_digipin(v.get('digipin', '')),
                'Type': v.get('validation_type', ''),
                'Status': v.get('status', ''),
                'Priority': v.get('priority', ''),
                'Agent': v.get('assigned_agent_id', 'N/A'),
                'Created': v.get('created_at', '')[:10] if v.get('created_at') else 'N/A'
            }
            for v in validations
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Bulk actions
        st.divider()
        st.markdown("#### Bulk Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_ids = st.multiselect(
                "Select Validations",
                options=[v.get('id') for v in validations]
            )
        
        with col2:
            new_status = st.selectbox(
                "New Status",
                options=["PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"]
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply Status Change"):
                if selected_ids:
                    for vid in selected_ids:
                        db.update_validation(vid, {'status': new_status})
                    st.success(f"✅ Updated {len(selected_ids)} validations")
                    st.rerun()
                else:
                    st.warning("Select validations first")
    else:
        st.info("📋 No validations found. Generate sample data or create new validations.")


# =============================================================================
# TAB 3: AGENT MANAGEMENT
# =============================================================================

with tab3:
    st.markdown("### 👥 Agent Management")
    
    # Search Section
    st.markdown("#### 🔍 Search Agent")
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input(
            "Search by Agent ID, Name, Email, or Phone",
            placeholder="Enter agent ID, name, email, or phone...",
            key="agent_search"
        )
    
    with search_col2:
        search_type = st.selectbox(
            "Search in",
            options=["All", "Agent ID", "Name", "Email", "Phone"],
            key="agent_search_type"
        )
    
    # Get all agents
    agents = db.get_all_agents()
    
    # Filter agents based on search
    filtered_agents = agents
    if search_query and agents:
        search_lower = search_query.lower()
        search_upper = search_query.upper()
        if search_type == "Agent ID":
            filtered_agents = [a for a in agents if search_upper in a.get('id', '').upper()]
        elif search_type == "Name":
            filtered_agents = [a for a in agents if search_lower in a.get('name', '').lower()]
        elif search_type == "Email":
            filtered_agents = [a for a in agents if search_lower in a.get('email', '').lower()]
        elif search_type == "Phone":
            filtered_agents = [a for a in agents if search_query in a.get('phone', '')]
        else:  # All
            filtered_agents = [
                a for a in agents 
                if search_lower in a.get('name', '').lower() 
                or search_lower in a.get('email', '').lower() 
                or search_query in a.get('phone', '')
                or search_upper in a.get('id', '').upper()
            ]
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"#### Agent List ({len(filtered_agents)} found)")
        
        if filtered_agents:
            for agent in filtered_agents:
                agent_id = agent.get('id', '')
                agent_name = agent.get('name', 'Unknown')
                
                with st.container():
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**{agent_name}**")
                        st.caption(f"🆔 `{agent_id}` | 📧 {agent.get('email', 'N/A')} | 📱 {agent.get('phone', 'N/A')}")
                        perf = agent.get('performance_score', 0) * 100
                        status = '✅ Active' if agent.get('active') else '❌ Inactive'
                        st.caption(f"📊 {perf:.0f}% | {status}")
                    
                    with col_actions:
                        col_pwd, col_del = st.columns(2)
                        
                        with col_pwd:
                            with st.popover("🔑"):
                                st.markdown(f"**Set Password for {agent_name}**")
                                new_pwd = st.text_input("New Password", type="password", key=f"pwd_{agent_id}")
                                confirm_pwd = st.text_input("Confirm Password", type="password", key=f"cpwd_{agent_id}")
                                if st.button("✅ Save", key=f"save_pwd_{agent_id}"):
                                    if new_pwd and confirm_pwd:
                                        if new_pwd == confirm_pwd:
                                            if len(new_pwd) >= 4:
                                                db.update_agent(agent_id, {'password': new_pwd})
                                                st.success("Password saved!")
                                                st.rerun()
                                            else:
                                                st.error("Min 4 characters!")
                                        else:
                                            st.error("Passwords don't match!")
                                    else:
                                        st.warning("Enter password")
                        
                        with col_del:
                            with st.popover("🗑️"):
                                st.warning(f"Delete **{agent_name}**?")
                                st.caption("This action cannot be undone.")
                                if st.button("✅ Yes, Delete", key=f"del_{agent_id}", type="primary"):
                                    if db.delete_agent(agent_id):
                                        st.success("Agent deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete")
                    
                    st.divider()
        elif search_query:
            st.warning(f"No agents found matching '{search_query}'")
        else:
            st.info("No agents registered")
    
    with col2:
        st.markdown("#### Add New Agent")
        
        with st.form("add_agent"):
            name = st.text_input("Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone")
            
            col_a, col_b = st.columns(2)
            with col_a:
                cert_date = st.date_input("Certification Date")
            with col_b:
                cert_expiry = st.date_input(
                    "Expiry Date",
                    value=datetime.now() + timedelta(days=365)
                )
            
            if st.form_submit_button("➕ Add Agent", use_container_width=True):
                if name and email:
                    try:
                        agent_id = db.create_agent({
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'certification_date': cert_date.isoformat(),
                            'certification_expiry': cert_expiry.isoformat(),
                            'active': 1,
                            'performance_score': 0.8
                        })
                        st.success(f"✅ Agent created: {agent_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.warning("Name and Email are required")
    
    # Agent performance overview
    if agents:
        st.divider()
        st.markdown("#### Agent Performance")
        
        perf_data = [
            {
                'Agent': a.get('name', ''),
                'Score': a.get('performance_score', 0) * 100
            }
            for a in agents
        ]
        
        fig = px.bar(
            pd.DataFrame(perf_data),
            x='Agent',
            y='Score',
            color='Score',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# TAB 4: SAMPLE DATA GENERATION
# =============================================================================

with tab4:
    st.markdown("### 🎲 Sample Data Generation")
    
    st.markdown("""
    Generate sample data for testing and demonstration purposes.
    This will create addresses, validations, deliveries, and agents.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Configuration")
        
        num_addresses = st.slider(
            "Number of Addresses",
            min_value=10,
            max_value=200,
            value=50,
            step=10
        )
        
        num_agents = st.slider(
            "Number of Agents",
            min_value=5,
            max_value=20,
            value=10
        )
        
        deliveries_per_address = st.slider(
            "Deliveries per Address",
            min_value=5,
            max_value=30,
            value=15
        )
        
        include_validations = st.checkbox("Generate Validations", value=True)
        include_verifications = st.checkbox("Generate Verifications", value=True)
    
    with col2:
        st.markdown("#### Cities Distribution")
        
        cities = [
            "New Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        
        for city in cities:
            st.checkbox(city, value=True, key=f"city_{city}")
    
    st.divider()
    
    if st.button("🚀 Generate Sample Data", type="primary"):
        progress = st.progress(0)
        status = st.empty()
        
        try:
            # Generate agents
            status.text("Creating agents...")
            agent_ids = []
            
            agent_names = [
                "Rahul Kumar", "Priya Sharma", "Amit Singh", "Neha Patel",
                "Vikram Reddy", "Anjali Gupta", "Rajesh Verma", "Sunita Devi",
                "Mohit Agarwal", "Kavita Nair", "Suresh Yadav", "Pooja Mishra",
                "Arun Krishnan", "Deepa Menon", "Sanjay Chauhan"
            ]
            
            for i in range(num_agents):
                name = agent_names[i % len(agent_names)]
                email = f"{name.lower().replace(' ', '.')}@aava.in"
                
                # Check if exists
                existing = db.get_agent_by_email(email)
                if existing:
                    agent_ids.append(existing['id'])
                else:
                    agent_id = db.create_agent({
                        'name': name,
                        'email': email,
                        'phone': f"+91-98{random.randint(10000000, 99999999)}",
                        'certification_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                        'certification_expiry': (datetime.now() + timedelta(days=random.randint(180, 365))).isoformat(),
                        'active': 1,
                        'performance_score': random.uniform(0.7, 0.95)
                    })
                    agent_ids.append(agent_id)
            
            progress.progress(0.2)
            
            # Generate addresses
            status.text("Creating addresses...")
            
            city_coords = {
                "New Delhi": (28.6139, 77.2090),
                "Mumbai": (19.0760, 72.8777),
                "Bangalore": (12.9716, 77.5946),
                "Chennai": (13.0827, 80.2707),
                "Kolkata": (22.5726, 88.3639),
                "Hyderabad": (17.3850, 78.4867),
                "Pune": (18.5204, 73.8567),
                "Ahmedabad": (23.0225, 72.5714),
                "Jaipur": (26.9124, 75.7873),
                "Lucknow": (26.8467, 80.9462)
            }
            
            selected_cities = [c for c in cities if st.session_state.get(f"city_{c}", True)]
            if not selected_cities:
                selected_cities = cities
            
            address_ids = []
            
            for i in range(num_addresses):
                city = selected_cities[i % len(selected_cities)]
                base_lat, base_lon = city_coords[city]
                
                # Add random offset
                lat = base_lat + random.uniform(-0.05, 0.05)
                lon = base_lon + random.uniform(-0.05, 0.05)
                
                # Generate DIGIPIN
                digipin_result = validator.encode(lat, lon)
                
                # Generate scores
                score = random.gauss(70, 15)
                score = max(0, min(100, score))
                grade = get_grade(score)
                
                # Create address
                address_id = db.create_address({
                    'digital_address': f"user{i+1}@{city.lower().replace(' ', '')}.in",
                    'digipin': digipin_result.digipin,
                    'descriptive_address': f"{random.randint(1, 999)} Sample Street, {city}",
                    'latitude': lat,
                    'longitude': lon,
                    'city': city,
                    'state': 'Sample State',
                    'pincode': f"{random.randint(100000, 999999)}",
                    'confidence_score': round(score, 2),
                    'confidence_grade': grade
                })
                address_ids.append(address_id)
                
                progress.progress(0.2 + 0.4 * (i + 1) / num_addresses)
            
            # Generate deliveries
            status.text("Creating delivery records...")
            
            for addr_id in address_ids:
                for j in range(deliveries_per_address):
                    addr = db.get_address(addr_id)
                    
                    status_choice = random.choices(
                        ['DELIVERED', 'DELIVERED_WITH_DIFFICULTY', 'FAILED'],
                        weights=[0.75, 0.15, 0.10]
                    )[0]
                    
                    db.create_delivery({
                        'address_id': addr_id,
                        'status': status_choice,
                        'actual_latitude': addr['latitude'] + random.gauss(0, 0.0002),
                        'actual_longitude': addr['longitude'] + random.gauss(0, 0.0002),
                        'ease_rating': random.randint(3, 5) if status_choice == 'DELIVERED' else None,
                        'delivery_partner': random.choice(['Partner A', 'Partner B', 'Partner C']),
                        'timestamp': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
                    })
            
            progress.progress(0.7)
            
            # Generate validations
            if include_validations:
                status.text("Creating validations...")
                
                for i, addr_id in enumerate(address_ids[:int(num_addresses * 0.7)]):
                    addr = db.get_address(addr_id)
                    
                    val_id = db.create_validation({
                        'address_id': addr_id,
                        'digital_address': addr.get('digital_address'),
                        'digipin': addr.get('digipin'),
                        'descriptive_address': addr.get('descriptive_address'),
                        'validation_type': random.choice(['PHYSICAL', 'DIGITAL', 'HYBRID']),
                        'status': random.choice(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'COMPLETED']),
                        'priority': random.choice(['LOW', 'NORMAL', 'NORMAL', 'HIGH', 'URGENT']),
                        'assigned_agent_id': random.choice(agent_ids) if agent_ids else None
                    })
                    
                    # Generate verification for completed ones
                    if include_verifications and random.random() > 0.3:
                        db.create_verification({
                            'validation_id': val_id,
                            'agent_id': random.choice(agent_ids) if agent_ids else 'AGT-001',
                            'verified': 1 if random.random() > 0.1 else 0,
                            'quality_score': random.uniform(0.7, 0.98),
                            'evidence_type': random.choice(['photo', 'photo+signature', 'video']),
                            'gps_latitude': addr['latitude'],
                            'gps_longitude': addr['longitude'],
                            'gps_accuracy': random.uniform(3, 15),
                            'notes': 'Sample verification'
                        })
            
            progress.progress(1.0)
            
            status.text("✅ Sample data generated successfully!")
            
            st.success(f"""
            ✅ **Sample Data Generated Successfully!**
            
            - 👥 **Agents:** {num_agents}
            - 📍 **Addresses:** {num_addresses}
            - 📦 **Deliveries:** {num_addresses * deliveries_per_address}
            - 📋 **Validations:** {int(num_addresses * 0.7) if include_validations else 0}
            """)
            
            # Log audit
            db.log_audit({
                'actor': 'admin',
                'action': 'sample_data.generated',
                'resource_type': 'system',
                'resource_id': 'bulk',
                'details': {
                    'addresses': num_addresses,
                    'agents': num_agents,
                    'deliveries': num_addresses * deliveries_per_address
                }
            })
        
        except Exception as e:
            st.error(f"❌ Error generating data: {str(e)}")
    
    # Clear data option
    st.divider()
    
    with st.expander("⚠️ Danger Zone"):
        st.warning("These actions are irreversible!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Validations"):
                # Would implement actual deletion
                st.warning("This would delete all validations (not implemented in demo)")
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                # Would implement actual deletion
                st.warning("This would delete all data (not implemented in demo)")


# =============================================================================
# TAB 5: AUDIT LOGS
# =============================================================================

with tab5:
    st.markdown("### 📝 Audit Logs")
    
    st.markdown("View system audit trail for all operations.")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        resource_filter = st.selectbox(
            "Resource Type",
            options=["All", "validation", "verification", "agent", "consent", "system"]
        )
    
    with col2:
        action_filter = st.text_input(
            "Action (contains)",
            placeholder="e.g., created, updated"
        )
    
    with col3:
        limit = st.slider("Show last N entries", 10, 200, 50)
    
    # Get logs
    logs = db.get_audit_logs(
        resource_type=resource_filter if resource_filter != "All" else None,
        limit=limit
    )
    
    if logs:
        for log in logs:
            action_icon = {
                'created': '➕',
                'updated': '✏️',
                'deleted': '🗑️',
                'submitted': '📤',
                'generated': '🎲'
            }
            
            action = log.get('action', '')
            icon = '📝'
            for key, val in action_icon.items():
                if key in action:
                    icon = val
                    break
            
            st.markdown(f"""
            <div style="background: white; padding: 0.75rem 1rem; border-radius: 8px; 
                        margin-bottom: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                        border-left: 3px solid #9c27b0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 1.2rem;">{icon}</span>
                        <strong style="margin-left: 0.5rem;">{action}</strong>
                    </div>
                    <span style="color: #666; font-size: 0.8rem;">{log.get('timestamp', '')}</span>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">
                    <span>Actor: {log.get('actor', 'N/A')}</span>
                    <span style="margin-left: 1rem;">Resource: {log.get('resource_type', '')}/{log.get('resource_id', '')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Export option
        st.divider()
        
        df = pd.DataFrame(logs)
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Audit Logs",
            csv,
            "audit_logs.csv",
            "text/csv"
        )
    else:
        st.info("📝 No audit logs found.")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    AAVA Admin Panel • System Version 1.0.0 • DHRUVA Ecosystem
</div>
""", unsafe_allow_html=True)
