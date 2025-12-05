# pages/10_🗺️_Central_Mapper.py
# AAVA - Central Mapper (CM) - DIGIPIN Registry
# Official DIGIPIN lookup and mapping service

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import DatabaseManager
from utils.digipin import DIGIPINValidator

st.set_page_config(
    page_title="Central Mapper - AAVA",
    page_icon="🗺️",
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
    [data-testid="stSidebarNav"] span { overflow: visible !important; text-overflow: clip !important; }
    .cm-stat {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .digipin-display {
        font-family: 'Courier New', monospace;
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .grid-cell {
        border: 1px solid #dee2e6;
        padding: 0.5rem;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); 
            padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <h1 style="margin: 0;">🗺️ Central Mapper (CM)</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
        DIGIPIN Registry • Geo-coordinate Mapping • Official Lookup Service
    </p>
</div>
""", unsafe_allow_html=True)

# Introduction
st.markdown("""
### What is Central Mapper?

**Central Mapper (CM)** is the official DIGIPIN registry service that:
- 🗺️ Maps geographic coordinates to DIGIPIN codes
- 📍 Provides DIGIPIN lookup and validation
- 🔗 Establishes the framework for AIPs and AIUs to access address data
- ✅ Ensures standardized geo-coding across India
""")

st.markdown("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 DIGIPIN Lookup",
    "📍 Coordinate Encoder", 
    "📊 DIGIPIN Registry",
    "📐 Grid Reference"
])

# ========== TAB 1: DIGIPIN LOOKUP ==========
with tab1:
    st.markdown("### 🔍 DIGIPIN Lookup Service")
    st.markdown("Enter a DIGIPIN to retrieve location and registry information")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        digipin_input = st.text_input(
            "Enter DIGIPIN",
            placeholder="e.g., 3PJK4M5L2T or 3PJ-K4M-5L2T",
            help="10-character DIGIPIN code"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        lookup_btn = st.button("🔍 Lookup", use_container_width=True, type="primary")
    
    if lookup_btn and digipin_input:
        # Validate and decode
        clean_digipin = digipin_input.replace('-', '').replace(' ', '').upper()
        
        if digipin_validator.validate(clean_digipin):
            result = digipin_validator.decode(clean_digipin)
            
            if result.valid:
                st.success("✅ Valid DIGIPIN")
                
                # Format DIGIPIN
                formatted = f"{clean_digipin[:3]}-{clean_digipin[3:6]}-{clean_digipin[6:]}"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### DIGIPIN Details")
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;">
                        <p class="digipin-display">{formatted}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    **Center Coordinates:**  
                    - Latitude: `{result.center_lat:.6f}°N`  
                    - Longitude: `{result.center_lon:.6f}°E`
                    
                    **Cell Bounds:**  
                    - Min Lat: {result.bounds['min_lat']:.6f}°  
                    - Max Lat: {result.bounds['max_lat']:.6f}°  
                    - Min Lon: {result.bounds['min_lon']:.6f}°  
                    - Max Lon: {result.bounds['max_lon']:.6f}°
                    
                    **Resolution:** ~{result.resolution_meters:.1f} meters
                    """)
                    
                    # Check if in registry
                    registered = db.get_address_by_digipin(clean_digipin)
                    if registered:
                        st.success(f"📚 **Registered in AIP Registry**")
                        st.markdown(f"""
                        - **Address ID:** {registered.get('id')}
                        - **Digital Address:** {registered.get('digital_address', 'N/A')}
                        - **Confidence Score:** {registered.get('confidence_score', 0):.0f}% ({registered.get('confidence_grade', 'F')})
                        """)
                    else:
                        st.info("📭 Not yet registered in AIP Registry")
                
                with col2:
                    st.markdown("#### Location Map")
                    
                    # Show map
                    map_data = pd.DataFrame({
                        'lat': [result.center_lat],
                        'lon': [result.center_lon]
                    })
                    st.map(map_data, zoom=15)
                    
                    # Get place name
                    try:
                        import requests
                        response = requests.get(
                            f"https://nominatim.openstreetmap.org/reverse",
                            params={
                                'lat': result.center_lat,
                                'lon': result.center_lon,
                                'format': 'json'
                            },
                            headers={'User-Agent': 'AAVA-CentralMapper/1.0'},
                            timeout=5
                        )
                        if response.status_code == 200:
                            place_data = response.json()
                            place_name = place_data.get('display_name', 'Unknown')
                            st.markdown(f"**📍 Location:** {place_name}")
                    except:
                        pass
            else:
                st.error(f"❌ {result.error}")
        else:
            st.error("❌ Invalid DIGIPIN format. Must be 10 characters using: 2,3,4,5,6,7,8,9,C,F,J,K,L,M,P,T")

# ========== TAB 2: COORDINATE ENCODER ==========
with tab2:
    st.markdown("### 📍 Coordinate to DIGIPIN Encoder")
    st.markdown("Convert geographic coordinates to DIGIPIN code")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        lat_input = st.number_input(
            "Latitude (°N)",
            min_value=2.5,
            max_value=38.5,
            value=28.6139,
            step=0.0001,
            format="%.6f",
            help="Range: 2.5° to 38.5° N"
        )
    
    with col2:
        lon_input = st.number_input(
            "Longitude (°E)",
            min_value=63.5,
            max_value=99.5,
            value=77.2090,
            step=0.0001,
            format="%.6f",
            help="Range: 63.5° to 99.5° E"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        encode_btn = st.button("📍 Generate DIGIPIN", use_container_width=True, type="primary")
    
    if encode_btn:
        result = digipin_validator.encode(lat_input, lon_input)
        
        if result.valid:
            formatted = f"{result.digipin[:3]}-{result.digipin[3:6]}-{result.digipin[6:]}"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                        padding: 2rem; border-radius: 12px; text-align: center; margin: 1rem 0;">
                <h3 style="margin: 0; color: #155724;">Generated DIGIPIN</h3>
                <p class="digipin-display" style="font-size: 3rem; margin: 1rem 0;">{formatted}</p>
                <p style="color: #155724;">Resolution: ~{result.resolution_meters:.1f} meters</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Encoding Details")
                st.markdown(f"""
                **Input Coordinates:**  
                - Latitude: {lat_input:.6f}°N  
                - Longitude: {lon_input:.6f}°E
                
                **Cell Center:**  
                - Latitude: {result.center_lat:.6f}°N  
                - Longitude: {result.center_lon:.6f}°E
                
                **Cell Bounds:**  
                - NW: ({result.bounds['max_lat']:.6f}°, {result.bounds['min_lon']:.6f}°)  
                - SE: ({result.bounds['min_lat']:.6f}°, {result.bounds['max_lon']:.6f}°)
                """)
            
            with col2:
                st.markdown("#### Location Map")
                map_data = pd.DataFrame({
                    'lat': [lat_input, result.center_lat],
                    'lon': [lon_input, result.center_lon]
                })
                st.map(map_data, zoom=18)
        else:
            st.error(f"❌ {result.error}")

# ========== TAB 3: DIGIPIN REGISTRY ==========
with tab3:
    st.markdown("### 📊 DIGIPIN Registry Statistics")
    
    # Get all registered DIGIPINs
    all_addresses = db.get_all_addresses(limit=1000)
    
    if all_addresses:
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="cm-stat">
                <h2 style="margin: 0;">{len(all_addresses)}</h2>
                <p style="margin: 0; opacity: 0.9;">Registered DIGIPINs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            unique_prefixes = len(set(a.get('digipin', '')[:3] for a in all_addresses if a.get('digipin')))
            st.markdown(f"""
            <div class="cm-stat">
                <h2 style="margin: 0;">{unique_prefixes}</h2>
                <p style="margin: 0; opacity: 0.9;">Unique L1-L3 Prefixes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            with_coords = len([a for a in all_addresses if a.get('latitude') and a.get('longitude')])
            st.markdown(f"""
            <div class="cm-stat">
                <h2 style="margin: 0;">{with_coords}</h2>
                <p style="margin: 0; opacity: 0.9;">Geo-located</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            verified = len([a for a in all_addresses if a.get('confidence_score', 0) >= 70])
            st.markdown(f"""
            <div class="cm-stat">
                <h2 style="margin: 0;">{verified}</h2>
                <p style="margin: 0; opacity: 0.9;">Verified</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # DIGIPIN distribution by prefix
        st.markdown("#### DIGIPIN Distribution by Level-1 Prefix")
        
        prefix_counts = {}
        for addr in all_addresses:
            digipin = addr.get('digipin', '')
            if digipin and len(digipin) >= 1:
                prefix = digipin[0]
                prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        
        if prefix_counts:
            import plotly.express as px
            sorted_prefixes = sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True)
            fig = px.bar(
                x=[p[0] for p in sorted_prefixes],
                y=[p[1] for p in sorted_prefixes],
                labels={'x': 'Level-1 Character', 'y': 'Count'},
                color=[p[1] for p in sorted_prefixes],
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Map of all DIGIPINs
        st.markdown("#### Registered DIGIPIN Locations")
        
        coords = [(a.get('latitude'), a.get('longitude')) for a in all_addresses 
                  if a.get('latitude') and a.get('longitude')]
        
        if coords:
            map_df = pd.DataFrame(coords, columns=['lat', 'lon'])
            st.map(map_df, zoom=4)
    else:
        st.info("📭 No DIGIPINs registered yet")

# ========== TAB 4: GRID REFERENCE ==========
with tab4:
    st.markdown("### 📐 DIGIPIN Grid Reference")
    st.markdown("Official DIGIPIN character grid used for encoding")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 4×4 Labeling Grid")
        st.markdown("""
        The DIGIPIN system uses a 4×4 grid with 16 unique characters:
        
        | | Col 0 | Col 1 | Col 2 | Col 3 |
        |--|-------|-------|-------|-------|
        | **Row 0** | F | C | 9 | 8 |
        | **Row 1** | J | 3 | 2 | 7 |
        | **Row 2** | K | 4 | 5 | 6 |
        | **Row 3** | L | M | P | T |
        
        - **Row 0** = Highest latitude (North)
        - **Row 3** = Lowest latitude (South)
        - **Col 0** = Lowest longitude (West)
        - **Col 3** = Highest longitude (East)
        """)
    
    with col2:
        st.markdown("#### DIGIPIN Specifications")
        st.markdown("""
        **Geographic Bounds (India):**
        - Latitude: 2.5°N to 38.5°N
        - Longitude: 63.5°E to 99.5°E
        
        **Character Set:**
        ```
        2, 3, 4, 5, 6, 7, 8, 9, C, F, J, K, L, M, P, T
        ```
        
        **Resolution by Level:**
        
        | Level | Grid Size | ~Distance |
        |-------|-----------|-----------|
        | 1 | 9° | 1000 km |
        | 2 | 2.25° | 250 km |
        | 3 | 33.75′ | 62.5 km |
        | 4 | 8.44′ | 15.6 km |
        | 5 | 2.11′ | 3.9 km |
        | 6 | 0.53′ | 1 km |
        | 7 | 0.13′ | 250 m |
        | 8 | 0.03′ | 60 m |
        | 9 | 0.5″ | 15 m |
        | 10 | 0.12″ | 3.8 m |
        """)
    
    st.markdown("---")
    
    # Interactive grid visualization
    st.markdown("#### Interactive Grid Explorer")
    st.markdown("Click a cell to see which character it represents")
    
    grid = [
        ['F', 'C', '9', '8'],
        ['J', '3', '2', '7'],
        ['K', '4', '5', '6'],
        ['L', 'M', 'P', 'T']
    ]
    
    # Display as buttons
    cols = st.columns(4)
    for col_idx in range(4):
        with cols[col_idx]:
            for row_idx in range(4):
                char = grid[row_idx][col_idx]
                if st.button(char, key=f"grid_{row_idx}_{col_idx}", use_container_width=True):
                    st.info(f"Character: **{char}** | Row: {row_idx} | Column: {col_idx}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.85rem;">
    <p>🗺️ Central Mapper (CM) - Official DIGIPIN Registry Service</p>
    <p>India Post • Department of Posts • DHRUVA Initiative</p>
</div>
""", unsafe_allow_html=True)
