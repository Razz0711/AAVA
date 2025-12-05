# pages/4_📊_Confidence_Score.py
# AAVA - Confidence Score Viewer
# View and analyze address confidence scores (Agent + Admin access)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_database
from utils.digipin import DIGIPINValidator
from utils.confidence_score import (
    ConfidenceScoreCalculator,
    AddressData,
    DeliveryRecord,
    PhysicalVerification,
    DeliveryStatus,
    get_grade_color,
    get_grade
)

st.set_page_config(
    page_title="Confidence Score - AAVA",
    page_icon="📊",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()
calculator = ConfidenceScoreCalculator()

# Initialize session states
if 'logged_in_agent' not in st.session_state:
    st.session_state.logged_in_agent = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Custom CSS - Apply BEFORE access check so sidebar looks consistent
st.markdown("""
<style>
    /* Sidebar - Wider to prevent text truncation */
    [data-testid="stSidebar"] { min-width: 280px !important; width: 280px !important; }
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; white-space: nowrap !important; }
    [data-testid="stSidebarNav"] span { font-size: 1.05rem !important; overflow: visible !important; text-overflow: clip !important; }
    
    .score-display {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .score-value {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1;
    }
    .grade-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 2rem;
        color: white;
        margin-top: 1rem;
    }
    .component-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 0.5rem;
    }
    .component-bar {
        height: 8px;
        border-radius: 4px;
        background: #e0e0e0;
        overflow: hidden;
    }
    .component-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# ACCESS CHECK - Agent OR Admin required
# =============================================================================

is_agent_logged_in = st.session_state.logged_in_agent is not None
is_admin_logged_in = st.session_state.admin_logged_in

if not is_agent_logged_in and not is_admin_logged_in:
    # Show login required message
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); 
                padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
        <h1 style="margin: 0;">📊 Confidence Score</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Login Required</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("🔐 **Login Required**")
    st.info("This page is accessible to **Agents** and **Admins** only.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Agent Login", use_container_width=True, type="primary"):
            st.switch_page("pages/3_📱_Agent_Portal.py")
    with col2:
        if st.button("⚙️ Admin Login", use_container_width=True):
            st.switch_page("pages/5_⚙️_Admin_Panel.py")
    
    st.stop()

# Determine user type for display
user_type = "Admin" if is_admin_logged_in else "Agent"
user_name = "Administrator" if is_admin_logged_in else st.session_state.logged_in_agent.get('name', 'Agent')

# Header with logged-in user info
st.markdown(f"""
<div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); 
            padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0;">📊 Confidence Score Viewer</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Analyze address reliability and confidence metrics</p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px;">
            <small style="opacity: 0.8;">Logged in as</small><br>
            <strong>{user_name}</strong>
            <span style="background: rgba(255,255,255,0.3); padding: 2px 8px; border-radius: 4px; margin-left: 8px; font-size: 0.8em;">{user_type}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search Address", "📈 Score Analysis", "📊 Batch Analysis"])

# =============================================================================
# TAB 1: SEARCH ADDRESS
# =============================================================================

with tab1:
    st.markdown("### 🔍 Search for Address Score")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_type = st.radio(
            "Search by:",
            options=["DIGIPIN", "Digital Address", "Address ID"],
            horizontal=True
        )
        
        if search_type == "DIGIPIN":
            search_value = st.text_input(
                "Enter DIGIPIN",
                placeholder="XXX-XXX-XXXX"
            ).upper()
        elif search_type == "Digital Address":
            search_value = st.text_input(
                "Enter Digital Address",
                placeholder="user@provider.in"
            )
        else:
            search_value = st.text_input(
                "Enter Address ID",
                placeholder="ADDR-XXXXXXXX"
            )
        
        search_btn = st.button("🔍 Search", type="primary")
    
    with col2:
        st.markdown("#### Quick Examples")
        
        # Get some addresses from DB
        sample_addresses = db.get_all_addresses(limit=5)
        
        if sample_addresses:
            for addr in sample_addresses:
                digipin = addr.get('digipin', 'N/A')
                if st.button(f"📍 {validator._format_digipin(digipin)}", key=f"sample_{addr.get('id')}"):
                    search_value = digipin
                    search_type = "DIGIPIN"
                    search_btn = True
        else:
            st.info("No addresses in database. Create addresses via Validation Request or User Portal.")
    
    st.divider()
    
    # Search results
    if search_btn and search_value:
        # Find the address
        address = None
        
        if search_type == "DIGIPIN":
            address = db.get_address_by_digipin(search_value)
        elif search_type == "Digital Address":
            address = db.get_address_by_digital_address(search_value)
        else:
            address = db.get_address(search_value)
        
        if address:
            st.success(f"✅ Address found: {address.get('id')}")
            
            # ============================================================
            # USE STORED DATABASE SCORE (NOT RECALCULATED)
            # ============================================================
            stored_score = float(address.get('confidence_score', 50))
            stored_grade = address.get('confidence_grade', 'C')
            
            # Determine grade if not stored
            if not stored_grade or stored_grade == 'F':
                if stored_score >= 90:
                    stored_grade = 'A+'
                elif stored_score >= 80:
                    stored_grade = 'A'
                elif stored_score >= 70:
                    stored_grade = 'B'
                elif stored_score >= 60:
                    stored_grade = 'C'
                elif stored_score >= 50:
                    stored_grade = 'D'
                else:
                    stored_grade = 'F'
            
            grade_descriptions = {
                'A+': 'Excellent - Highly Reliable',
                'A': 'Very Good - Reliable',
                'B': 'Good - Mostly Reliable',
                'C': 'Fair - Moderately Reliable',
                'D': 'Poor - Low Reliability',
                'F': 'Fail - Unreliable'
            }
            grade_description = grade_descriptions.get(stored_grade, 'Unknown')
            
            # Display results using STORED score
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Score gauge
                grade_color = {
                    'A+': '#00897b', 'A': '#4CAF50', 'B': '#8BC34A', 
                    'C': '#FFC107', 'D': '#FF9800', 'F': '#f44336'
                }.get(stored_grade, '#9e9e9e')
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=stored_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confidence Score (from Database)", 'font': {'size': 24}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': grade_color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(244, 67, 54, 0.3)'},
                            {'range': [50, 70], 'color': 'rgba(255, 193, 7, 0.3)'},
                            {'range': [70, 90], 'color': 'rgba(76, 175, 80, 0.3)'},
                            {'range': [90, 100], 'color': 'rgba(0, 150, 136, 0.3)'}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': stored_score
                        }
                    }
                ))
                fig.update_layout(
                    height=350,
                    margin=dict(l=30, r=30, t=50, b=30)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Grade display
                st.markdown(f"""
                <div style="text-align: center; margin-top: -1rem;">
                    <span class="grade-badge" style="background: {grade_color};">
                        {stored_grade}
                    </span>
                    <p style="color: #666; margin-top: 0.5rem;">{grade_description}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Address Details
            st.markdown("### 📋 Address Details")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **DIGIPIN:** `{address.get('digipin', 'N/A')}`  
                **Digital Address:** {address.get('digital_address', 'N/A')}  
                **Descriptive:** {address.get('descriptive_address', 'N/A')}  
                **City:** {address.get('city', 'N/A')}  
                **State:** {address.get('state', 'N/A')}  
                **Pincode:** {address.get('pincode', 'N/A')}
                """)
            
            with col2:
                st.markdown(f"""
                **Latitude:** {address.get('latitude', 'N/A')}  
                **Longitude:** {address.get('longitude', 'N/A')}  
                **Created:** {address.get('created_at', 'N/A')[:10] if address.get('created_at') else 'N/A'}  
                **Updated:** {address.get('updated_at', 'N/A')[:10] if address.get('updated_at') else 'N/A'}
                """)
            
            st.divider()
            
            # Verification History
            st.markdown("### ✅ Verification History")
            
            # Get verifications for this address
            verifications = db.get_verifications_for_address(address.get('id'))
            
            if verifications:
                for ver in verifications:
                    status_icon = "✅" if ver.get('verified') else "❌"
                    st.markdown(f"""
                    - {status_icon} **{ver.get('id')}** - Quality: {ver.get('quality_score', 0)*100:.0f}% - 
                    Agent: {ver.get('agent_id', 'N/A')} - Date: {ver.get('timestamp', 'N/A')[:10] if ver.get('timestamp') else 'N/A'}
                    """)
            else:
                st.info("No verifications recorded yet. Request verification from User Portal.")
            
            st.divider()
            
            # Score explanation
            st.markdown("### 📊 Score Components (Explanation)")
            st.markdown("""
            The confidence score is calculated based on 4 weighted components:
            
            | Component | Weight | Description |
            |-----------|--------|-------------|
            | **Delivery Success Rate (DSR)** | 30% | Based on historical delivery outcomes |
            | **Spatial Consistency (SC)** | 30% | How accurately deliveries match stated coordinates |
            | **Temporal Freshness (TF)** | 20% | Time since last successful verification |
            | **Physical Verification (PVS)** | 20% | Agent verification status and quality |
            
            **How to improve your score:**
            - ✅ Get your address verified by an agent (+15-20%)
            - 📦 Successful deliveries improve DSR
            - 📍 Consistent GPS coordinates improve SC
            - ⏱️ Recent activity improves TF
            """)
        
        else:
            st.error("❌ Address not found. Please check the search value.")
            st.info("💡 Try searching with a different identifier.")


# =============================================================================
# TAB 2: SCORE ANALYSIS
# =============================================================================

with tab2:
    st.markdown("### 📈 Score Component Analysis")
    
    st.markdown("""
    Understand how each component affects the confidence score with interactive simulations.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Adjust Parameters")
        
        # Delivery success rate
        delivery_success = st.slider(
            "Delivery Success Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.80,
            step=0.05,
            help="Percentage of successful deliveries"
        )
        
        # Spatial variance
        spatial_variance = st.slider(
            "Spatial Variance (meters)",
            min_value=0,
            max_value=100,
            value=15,
            step=5,
            help="Average distance from stated location"
        )
        
        # Days since last verification
        days_since = st.slider(
            "Days Since Last Event",
            min_value=0,
            max_value=365,
            value=30,
            step=7,
            help="Days since last successful delivery/verification"
        )
        
        # Physical verification
        has_physical = st.checkbox("Has Physical Verification", value=True)
        
        if has_physical:
            verification_quality = st.slider(
                "Verification Quality",
                min_value=0.5,
                max_value=1.0,
                value=0.90,
                step=0.05
            )
        else:
            verification_quality = 0.0
    
    with col2:
        # Generate sample data based on parameters
        import numpy as np
        
        # Create deliveries
        num_deliveries = 20
        delivery_records = []
        
        for i in range(num_deliveries):
            # Determine status based on success rate
            if random.random() < delivery_success * 0.85:
                status = DeliveryStatus.DELIVERED
            elif random.random() < delivery_success:
                status = DeliveryStatus.DELIVERED_WITH_DIFFICULTY
            else:
                status = DeliveryStatus.FAILED
            
            # Add coordinate with variance
            variance_deg = spatial_variance / 111320  # Convert meters to degrees
            
            delivery_records.append(DeliveryRecord(
                id=f"SIM-{i:04d}",
                timestamp=datetime.now() - timedelta(days=random.randint(0, 365)),
                status=status,
                actual_lat=28.6139 + random.gauss(0, variance_deg),
                actual_lon=77.2090 + random.gauss(0, variance_deg),
                ease_rating=random.randint(3, 5) if status == DeliveryStatus.DELIVERED else None
            ))
        
        # Add one recent event
        delivery_records.append(DeliveryRecord(
            id="SIM-RECENT",
            timestamp=datetime.now() - timedelta(days=days_since),
            status=DeliveryStatus.DELIVERED,
            actual_lat=28.6139,
            actual_lon=77.2090,
            ease_rating=5
        ))
        
        # Create verification if enabled
        verification_records = []
        if has_physical:
            verification_records.append(PhysicalVerification(
                id="VER-SIM",
                agent_id="AGT-001",
                timestamp=datetime.now() - timedelta(days=days_since),
                verified=True,
                quality_score=verification_quality,
                evidence_type="photo",
                gps_accuracy=5.0
            ))
        
        # Create address data
        sim_address = AddressData(
            address_id="SIM-ADDR",
            stated_lat=28.6139,
            stated_lon=77.2090,
            created_at=datetime.now() - timedelta(days=365),
            deliveries=delivery_records,
            verifications=verification_records
        )
        
        # Calculate score
        sim_result = calculator.calculate(sim_address)
        
        # Display gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sim_result.score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Simulated Score", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': get_grade_color(sim_result.grade)},
                'steps': [
                    {'range': [0, 50], 'color': "rgba(244, 67, 54, 0.2)"},
                    {'range': [50, 70], 'color': "rgba(255, 193, 7, 0.2)"},
                    {'range': [70, 90], 'color': "rgba(76, 175, 80, 0.2)"},
                    {'range': [90, 100], 'color': "rgba(0, 150, 136, 0.2)"}
                ]
            }
        ))
        fig.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=30))
        st.plotly_chart(fig, use_container_width=True)
        
        # Component bars
        st.markdown(f"**Grade: {sim_result.grade}** - {sim_result.grade_description}")
        
        for key, comp in sim_result.components.items():
            color = get_grade_color(get_grade(comp.raw_value * 100))
            st.markdown(f"""
            **{comp.name}**: {comp.raw_value:.1%}
            """)
            st.progress(comp.raw_value)
    
    st.divider()
    
    # Score formula explanation
    st.markdown("### 📐 Score Formula")
    
    st.latex(r"""
    Score = 100 \times \sum_{i=1}^{4} (Component_i \times Weight_i)
    """)
    
    st.markdown("""
    | Component | Weight | Formula |
    |-----------|--------|---------|
    | Delivery Success Rate (DSR) | 30% | $\\frac{\\sum points}{N \\times 100}$ |
    | Spatial Consistency (SC) | 30% | $e^{-(\\frac{avg\\_dist}{ref\\_dist})^2}$ |
    | Temporal Freshness (TF) | 20% | $e^{-\\lambda \\times days}$ where $\\lambda = \\frac{ln(2)}{half\\_life}$ |
    | Physical Verification (PVS) | 20% | $verified \\times quality \\times freshness$ |
    """)


# =============================================================================
# TAB 3: BATCH ANALYSIS
# =============================================================================

with tab3:
    st.markdown("### 📊 Batch Score Analysis")
    
    st.markdown("Analyze confidence scores across multiple addresses.")
    
    # Get all addresses
    all_addresses = db.get_all_addresses(limit=200)
    
    if len(all_addresses) >= 5:
        # Generate scores for all
        scores_data = []
        
        for addr in all_addresses:
            # Quick score calculation (or use stored score)
            score = addr.get('confidence_score', 0)
            grade = addr.get('confidence_grade', 'F')
            
            # If no score, generate sample
            if score == 0:
                score = random.gauss(70, 15)
                score = max(0, min(100, score))
                grade = get_grade(score)
            
            scores_data.append({
                'Address ID': addr.get('id', ''),
                'DIGIPIN': validator._format_digipin(addr.get('digipin', '')),
                'City': addr.get('city', 'N/A'),
                'Score': round(score, 1),
                'Grade': grade
            })
        
        df = pd.DataFrame(scores_data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Addresses", len(df))
        
        with col2:
            st.metric("Average Score", f"{df['Score'].mean():.1f}")
        
        with col3:
            high_quality = len(df[df['Score'] >= 70])
            st.metric("High Quality (≥70)", f"{high_quality} ({high_quality/len(df)*100:.0f}%)")
        
        with col4:
            low_quality = len(df[df['Score'] < 50])
            st.metric("Low Quality (<50)", f"{low_quality} ({low_quality/len(df)*100:.0f}%)")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Score Distribution")
            
            fig = px.histogram(
                df, x='Score',
                nbins=20,
                color_discrete_sequence=['#2196F3']
            )
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Grade Distribution")
            
            grade_counts = df['Grade'].value_counts().to_dict()
            
            fig = px.pie(
                values=list(grade_counts.values()),
                names=list(grade_counts.keys()),
                color=list(grade_counts.keys()),
                color_discrete_map={
                    'A+': '#00C853', 'A': '#00E676', 'B': '#FFEB3B',
                    'C': '#FFC107', 'D': '#FF9800', 'F': '#F44336'
                }
            )
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Filterable table
        st.markdown("#### Address Scores Table")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            grade_filter = st.multiselect(
                "Filter by Grade",
                options=['A+', 'A', 'B', 'C', 'D', 'F'],
                default=['A+', 'A', 'B', 'C', 'D', 'F']
            )
        
        with col2:
            city_filter = st.multiselect(
                "Filter by City",
                options=df['City'].unique().tolist()
            )
        
        # Apply filters
        filtered_df = df[df['Grade'].isin(grade_filter)]
        if city_filter:
            filtered_df = filtered_df[filtered_df['City'].isin(city_filter)]
        
        st.dataframe(
            filtered_df.sort_values('Score', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download as CSV",
            csv,
            "confidence_scores.csv",
            "text/csv"
        )
    
    else:
        st.info("📊 Need at least 5 addresses for batch analysis. Create addresses via Validation Request or User Portal.")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    AAVA • Confidence Score System • DHRUVA Ecosystem
</div>
""", unsafe_allow_html=True)
