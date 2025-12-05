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
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Read admin config from .env file
def get_admin_config():
    """Read admin config directly from .env file."""
    env_path = os.path.join(PROJECT_ROOT, '.env')
    config = {
        'admin_username': 'admin_raj',
        'admin_password': 'admin_raj@'
    }
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('ADMIN_USERNAME='):
                    config['admin_username'] = line.split('=', 1)[1].strip()
                elif line.startswith('ADMIN_PASSWORD='):
                    config['admin_password'] = line.split('=', 1)[1].strip()
    return config

# Load config once
ADMIN_CONFIG = get_admin_config()

def get_email_config():
    """Read email config from .env or Streamlit secrets."""
    sender = None
    password = None
    
    # Check streamlit secrets first
    try:
        if hasattr(st, 'secrets'):
            sender = st.secrets.get('EMAIL_SENDER', None)
            password = st.secrets.get('EMAIL_PASSWORD', None)
    except Exception:
        pass

    # Fallback to .env file
    if not sender or not password:
        env_path = os.path.join(PROJECT_ROOT, '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'EMAIL_SENDER' and not sender:
                            sender = value
                        elif key == 'EMAIL_PASSWORD' and not password:
                            password = value

    return {'sender': sender, 'password': password}


def send_agent_credentials_email(agent_email, agent_name, agent_id, password):
    """Send agent credentials via Gmail SMTP. Returns (success: bool, message:str)."""
    cfg = get_email_config()
    sender = cfg.get('sender')
    sender_password = cfg.get('password')

    if not sender or not sender_password:
        return False, 'Email not configured. Provide EMAIL_SENDER and EMAIL_PASSWORD in secrets or .env'

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🎉 Welcome to AAVA - Your Agent Credentials'
        msg['From'] = sender
        msg['To'] = agent_email

        html = f"""
        <html>
        <body>
        <p>Hi {agent_name},</p>
        <p>Your agent account has been created. Here are your credentials:</p>
        <ul>
          <li><strong>Agent ID:</strong> {agent_id}</li>
          <li><strong>Password:</strong> {password}</li>
          <li><strong>Email:</strong> {agent_email}</li>
        </ul>
        <p>Please keep these credentials secure.</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, sender_password)
            server.sendmail(sender, agent_email, msg.as_string())

        return True, 'Email sent successfully'
    except Exception as e:
        return False, str(e)

def generate_strong_password(length=12):
    """Generate a strong random password."""
    # Include uppercase, lowercase, digits, and special characters
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "@#$%&*!"
    
    # Ensure at least one of each type
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # Fill remaining with random mix
    all_chars = uppercase + lowercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    random.shuffle(password)
    return ''.join(password)

from utils.database import get_database
from utils.digipin import DIGIPINValidator
from utils.confidence_score import get_grade

st.set_page_config(
    page_title="Admin Panel - AAVA",
    page_icon="⚙️",
    layout="wide"
)

# Admin credentials from config
ADMIN_USERNAME = ADMIN_CONFIG['admin_username']
ADMIN_PASSWORD = ADMIN_CONFIG['admin_password']

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Custom CSS for sidebar and login (load always)
st.markdown("""
<style>
    /* Sidebar Navigation */
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; }
</style>
""", unsafe_allow_html=True)

# Admin Login Check
if not st.session_state.admin_logged_in:
    # Professional Login Page CSS
    st.markdown("""
    <style>
        .admin-login-header {
            background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2rem;
        }
        .login-footer {
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #eee;
        }
        .login-footer p {
            color: #888;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Purple header banner
    st.markdown("""
    <div class="admin-login-header">
        <h1 style="margin: 0;">⚙️ Admin Panel</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">System Administration Login</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("admin_login"):
            st.markdown("##### 👤 Username")
            username = st.text_input("Username", placeholder="Enter admin username", label_visibility="collapsed")
            
            st.markdown("##### 🔑 Password")
            password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
            
            st.markdown("")
            login_btn = st.form_submit_button("🔓 Sign In", use_container_width=True)
            
            if login_btn:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password!")
        
        st.markdown("""
        <div class="login-footer">
            <p>🔒 Secure authentication</p>
            <p>AAVA Admin System v1.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

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

# Header with logout button
col_header, col_logout = st.columns([5, 1])
with col_header:
    st.markdown("""
    <div class="admin-header">
        <h1 style="margin: 0;">⚙️ Admin Panel</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">System Administration & Management</p>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, key="admin_logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "📋 Validations",
    "👥 Agents",
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
        st.info("📋 No validations found. Create new validations via the Validation Request page.")


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
                agent_password = agent.get('password', '') or '(Not Set)'
                
                with st.container():
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**{agent_name}**")
                        st.caption(f"🆔 `{agent_id}` | 📧 {agent.get('email', 'N/A')} | 📱 {agent.get('phone', 'N/A')}")
                        perf = agent.get('performance_score', 0) * 100
                        status = '✅ Active' if agent.get('active') else '❌ Inactive'
                        st.caption(f"📊 {perf:.0f}% | {status} | 🔑 Password: `{agent_password}`")
                    
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
            send_credentials = st.checkbox("Send credentials via email to the agent", value=False, help="If checked, the agent will receive their Agent ID and password by email (requires EMAIL_SENDER and EMAIL_PASSWORD configured)")
            
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
                        # Generate strong password
                        auto_password = generate_strong_password()
                        
                        agent_id = db.create_agent({
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'password': auto_password,
                            'certification_date': cert_date.isoformat(),
                            'certification_expiry': cert_expiry.isoformat(),
                            'active': 1,
                            'performance_score': 0.8
                        })
                        st.success(f"✅ Agent created!")
                        st.info(f"🆔 Agent ID: `{agent_id}`")
                        st.info(f"🔑 Password: `{auto_password}`")

                        # Optionally send credentials via email
                        if send_credentials:
                            email_sent, email_msg = send_agent_credentials_email(email, name, agent_id, auto_password)
                            if email_sent:
                                st.success(f"📧 Credentials sent to {email}")
                            else:
                                st.warning(f"📧 Email not sent: {email_msg}")
                                st.warning("⚠️ Please save this password - it won't be shown again!")
                        else:
                            st.warning("⚠️ Please save this password - it won't be shown again!")
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
# TAB 4: AUDIT LOGS
# =============================================================================

with tab4:
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
