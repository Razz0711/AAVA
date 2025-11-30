# pages/4_📊_Confidence_Score.py
# AAVA - Confidence Score Viewer
# View and analyze address confidence scores

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
    SampleDataGenerator,
    AddressData,
    DeliveryRecord,
    PhysicalVerification,
    DeliveryStatus,
    get_grade_color,
    get_grade
)
from utils.premium_theme import PREMIUM_CSS, PAGE_GRADIENTS

st.set_page_config(
    page_title="Confidence Score - AAVA",
    page_icon="📊",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()
calculator = ConfidenceScoreCalculator()

# Apply Premium Theme
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# Premium Header
st.markdown(f"""
<div class="premium-header" style="background: linear-gradient(135deg, {PAGE_GRADIENTS['confidence'][0]} 0%, {PAGE_GRADIENTS['confidence'][1]} 50%, {PAGE_GRADIENTS['confidence'][2]} 100%);">
    <h1 style="margin: 0; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 2rem;">📊</span> Confidence Score Viewer
    </h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">Analyze address reliability and confidence metrics</p>
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
            st.info("No addresses in database. Generate sample data from Admin Panel.")
    
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
            
            # Get delivery history for this address
            deliveries = db.get_deliveries_by_address(address.get('id'))
            
            # Get verifications through validations
            validations = db.get_all_validations(limit=100)
            address_validations = [
                v for v in validations 
                if v.get('address_id') == address.get('id')
            ]
            
            verifications = []
            for val in address_validations:
                ver_list = db.get_verifications_by_validation(val.get('id'))
                verifications.extend(ver_list)
            
            # Build AddressData object
            delivery_records = []
            for d in deliveries:
                try:
                    status_str = d.get('status', 'PENDING')
                    status = DeliveryStatus[status_str] if status_str in DeliveryStatus.__members__ else DeliveryStatus.PENDING
                    
                    delivery_records.append(DeliveryRecord(
                        id=d.get('id', ''),
                        timestamp=datetime.fromisoformat(d.get('timestamp', datetime.now().isoformat())),
                        status=status,
                        actual_lat=d.get('actual_latitude'),
                        actual_lon=d.get('actual_longitude'),
                        ease_rating=d.get('ease_rating')
                    ))
                except:
                    pass
            
            verification_records = []
            for v in verifications:
                try:
                    verification_records.append(PhysicalVerification(
                        id=v.get('id', ''),
                        agent_id=v.get('agent_id', ''),
                        timestamp=datetime.fromisoformat(v.get('timestamp', datetime.now().isoformat())),
                        verified=bool(v.get('verified')),
                        quality_score=v.get('quality_score', 0.8),
                        evidence_type=v.get('evidence_type', 'photo'),
                        gps_accuracy=v.get('gps_accuracy', 10)
                    ))
                except:
                    pass
            
            # If no real data, generate sample for demo
            if not delivery_records:
                st.info("📊 No delivery history found. Generating sample data for demonstration...")
                
                # Generate sample deliveries
                for i in range(random.randint(8, 15)):
                    days_ago = random.randint(1, 180)
                    status = random.choices(
                        [DeliveryStatus.DELIVERED, DeliveryStatus.DELIVERED_WITH_DIFFICULTY, DeliveryStatus.FAILED],
                        weights=[0.75, 0.15, 0.10]
                    )[0]
                    
                    delivery_records.append(DeliveryRecord(
                        id=f"DEL-{i:04d}",
                        timestamp=datetime.now() - timedelta(days=days_ago),
                        status=status,
                        actual_lat=address.get('latitude', 28.6) + random.gauss(0, 0.0001),
                        actual_lon=address.get('longitude', 77.2) + random.gauss(0, 0.0001),
                        ease_rating=random.randint(3, 5) if status == DeliveryStatus.DELIVERED else None
                    ))
            
            if not verification_records and random.random() > 0.3:
                verification_records.append(PhysicalVerification(
                    id="VER-DEMO",
                    agent_id="AGT-001",
                    timestamp=datetime.now() - timedelta(days=random.randint(30, 120)),
                    verified=True,
                    quality_score=random.uniform(0.75, 0.95),
                    evidence_type="photo",
                    gps_accuracy=random.uniform(3, 10)
                ))
            
            # Create address data object
            address_data = AddressData(
                address_id=address.get('id', 'UNKNOWN'),
                stated_lat=address.get('latitude', 28.6139),
                stated_lon=address.get('longitude', 77.2090),
                created_at=datetime.fromisoformat(address.get('created_at', datetime.now().isoformat())) 
                    if address.get('created_at') else datetime.now() - timedelta(days=180),
                deliveries=delivery_records,
                verifications=verification_records
            )
            
            # Calculate score
            result = calculator.calculate(address_data)
            
            # Display results
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                # Score gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result.score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Confidence Score", 'font': {'size': 24}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': get_grade_color(result.grade)},
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
                            'value': result.score
                        }
                    }
                ))
                fig.update_layout(
                    height=350,
                    margin=dict(l=30, r=30, t=50, b=30)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Grade display
                grade_color = get_grade_color(result.grade)
                st.markdown(f"""
                <div style="text-align: center; margin-top: -1rem;">
                    <span class="grade-badge" style="background: {grade_color};">
                        {result.grade}
                    </span>
                    <p style="color: #666; margin-top: 0.5rem;">{result.grade_description}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Component breakdown
            st.markdown("### 📊 Score Components")
            
            cols = st.columns(4)
            
            component_icons = {
                'delivery_success': '📦',
                'spatial_consistency': '📍',
                'temporal_freshness': '⏱️',
                'physical_verification': '✅'
            }
            
            for i, (key, comp) in enumerate(result.components.items()):
                with cols[i]:
                    icon = component_icons.get(key, '📊')
                    color = get_grade_color(get_grade(comp.raw_value * 100))
                    
                    st.markdown(f"""
                    <div class="component-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.5rem;">{icon}</span>
                            <span style="font-size: 1.5rem; font-weight: 700; color: {color};">
                                {comp.raw_value:.0%}
                            </span>
                        </div>
                        <h4 style="margin: 0.5rem 0; font-size: 0.9rem;">{comp.name}</h4>
                        <div class="component-bar">
                            <div class="component-fill" style="width: {comp.raw_value*100}%; background: {color};"></div>
                        </div>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #666;">
                            Weight: {comp.weight:.0%} • Weighted: {comp.weighted_value:.3f}
                        </p>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.7rem; color: #999;">
                            {comp.description[:50]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            # Additional details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📦 Delivery History")
                
                if delivery_records:
                    # Create dataframe
                    df = pd.DataFrame([
                        {
                            'Date': d.timestamp.strftime('%Y-%m-%d'),
                            'Status': d.status.value,
                            'Rating': d.ease_rating or 'N/A'
                        }
                        for d in sorted(delivery_records, key=lambda x: x.timestamp, reverse=True)
                    ])
                    
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Status pie chart
                    status_counts = {}
                    for d in delivery_records:
                        status_counts[d.status.value] = status_counts.get(d.status.value, 0) + 1
                    
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        color_discrete_sequence=['#4CAF50', '#FF9800', '#F44336']
                    )
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No delivery history")
            
            with col2:
                st.markdown("#### 📍 Address Details")
                
                # Display DIGIPIN
                digipin = address.get('digipin', '')
                if digipin:
                    st.markdown(f"""
                    <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px; text-align: center;">
                        <span style="font-family: monospace; font-size: 1.5rem; font-weight: 700;">
                            {validator._format_digipin(digipin)}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                **ID:** {address.get('id', 'N/A')}  
                **Digital Address:** {address.get('digital_address') or 'Not set'}  
                **City:** {address.get('city') or 'N/A'}  
                **State:** {address.get('state') or 'N/A'}  
                **PIN Code:** {address.get('pincode') or 'N/A'}
                """)
                
                # Map
                if address.get('latitude') and address.get('longitude'):
                    fig = go.Figure(go.Scattermapbox(
                        lat=[address.get('latitude')],
                        lon=[address.get('longitude')],
                        mode='markers',
                        marker=go.scattermapbox.Marker(size=14, color='red'),
                        text=[validator._format_digipin(digipin)],
                        hoverinfo='text'
                    ))
                    
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox=dict(
                            center=dict(lat=address.get('latitude'), lon=address.get('longitude')),
                            zoom=15
                        ),
                        margin={"r":0,"t":0,"l":0,"b":0},
                        height=200
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            if result.recommendations:
                st.markdown("#### 💡 Recommendations")
                for rec in result.recommendations:
                    st.markdown(f"- {rec}")
        
        else:
            st.error("❌ Address not found. Please check the search value.")
            st.info("💡 Try searching with a different identifier or generate sample data from Admin Panel.")


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
        st.info("📊 Need at least 5 addresses for batch analysis. Generate sample data from Admin Panel!")
        
        if st.button("🎲 Generate Sample Data"):
            st.info("Please go to Admin Panel → Sample Data Generation")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    AAVA • Confidence Score System • DHRUVA Ecosystem
</div>
""", unsafe_allow_html=True)
