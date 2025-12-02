# pages/7_🔍_Public_Verify.py
# AAVA - Public DIGIPIN Verification Page
# Public access - No login required

import streamlit as st
import sys
import os
import folium
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.digipin import DIGIPINValidator

st.set_page_config(
    page_title="Public Verify - AAVA",
    page_icon="🔍",
    layout="wide"
)

# Initialize
validator = DIGIPINValidator()

# Custom CSS
st.markdown("""
<style>
    /* Sidebar Navigation */
    [data-testid="stSidebarNav"] ul { padding-top: 1rem; }
    [data-testid="stSidebarNav"] li { margin-bottom: 0.5rem; }
    [data-testid="stSidebarNav"] a { font-size: 1.05rem !important; padding: 0.6rem 1rem !important; }
    
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .success-result {
        border-left: 4px solid #4CAF50;
        background: #e8f5e9;
    }
    .error-result {
        border-left: 4px solid #f44336;
        background: #ffebee;
    }
    .info-result {
        border-left: 4px solid #2196F3;
        background: #e3f2fd;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        height: 100%;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 1.5rem 2rem; border-radius: 12px; color: white; margin-bottom: 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0;">🔍 Public DIGIPIN Services</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Verify, Convert & Lookup DIGIPIN codes - Free for everyone</p>
        </div>
        <div style="text-align: right; background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 8px;">
            <small style="opacity: 0.8;">🌐 Public Access</small><br>
            <strong>No Login Required</strong>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Info banner
st.markdown("""
<div class="info-result" style="padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
    <strong>ℹ️ What is DIGIPIN?</strong><br>
    DIGIPIN is a 10-character geo-coded address system for India. Each code represents a unique ~4m x 4m area, 
    making it easy to locate any place precisely. Format: <code>XXX-XXX-XXXX</code>
</div>
""", unsafe_allow_html=True)

# Tabs for different services
tab1, tab2, tab3 = st.tabs(["✅ Verify DIGIPIN", "📍 Address → DIGIPIN", "🗺️ DIGIPIN → Location"])

# =============================================================================
# TAB 1: VERIFY DIGIPIN
# =============================================================================
with tab1:
    st.markdown("### ✅ Verify DIGIPIN Code")
    st.markdown("Enter a DIGIPIN code to check if it's valid and see its location.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        digipin_input = st.text_input(
            "Enter DIGIPIN",
            placeholder="e.g., 3PJ-K4M-5L2T or 3PJK4M5L2T",
            max_chars=14,
            key="verify_digipin"
        )
        
        verify_btn = st.button("🔍 Verify DIGIPIN", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f5f5f5; padding: 1rem; border-radius: 8px; font-size: 0.9em;">
            <strong>Valid Characters:</strong><br>
            <code>2 3 4 5 6 7 8 9</code><br>
            <code>C F J K L M P T</code><br><br>
            <strong>Format:</strong> 10 characters
        </div>
        """, unsafe_allow_html=True)
    
    if verify_btn and digipin_input:
        # Validate format
        is_valid, message = validator.validate_with_details(digipin_input)
        
        if is_valid:
            # Decode to get coordinates
            result = validator.decode(digipin_input)
            
            if result.valid:
                st.markdown("---")
                
                # Success message
                st.success("✅ **Valid DIGIPIN!**")
                
                col_info, col_map = st.columns([1, 1])
                
                with col_info:
                    st.markdown(f"""
                    <div class="result-card success-result">
                        <h4 style="margin-top: 0;">📋 DIGIPIN Details</h4>
                        <table style="width: 100%;">
                            <tr><td><strong>Code:</strong></td><td><code>{result.formatted}</code></td></tr>
                            <tr><td><strong>Latitude:</strong></td><td>{result.center_lat:.6f}°</td></tr>
                            <tr><td><strong>Longitude:</strong></td><td>{result.center_lon:.6f}°</td></tr>
                            <tr><td><strong>Resolution:</strong></td><td>~{result.resolution_meters:.1f} meters</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bounds info
                    st.markdown(f"""
                    <div class="result-card info-result">
                        <h4 style="margin-top: 0;">📐 Cell Bounds</h4>
                        <small>
                        <strong>North:</strong> {result.bounds['max_lat']:.6f}°<br>
                        <strong>South:</strong> {result.bounds['min_lat']:.6f}°<br>
                        <strong>East:</strong> {result.bounds['max_lon']:.6f}°<br>
                        <strong>West:</strong> {result.bounds['min_lon']:.6f}°
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_map:
                    # Create map
                    m = folium.Map(
                        location=[result.center_lat, result.center_lon],
                        zoom_start=18,
                        tiles="OpenStreetMap"
                    )
                    
                    # Add marker
                    folium.Marker(
                        [result.center_lat, result.center_lon],
                        popup=f"DIGIPIN: {result.formatted}",
                        icon=folium.Icon(color='green', icon='check')
                    ).add_to(m)
                    
                    # Add rectangle for bounds
                    folium.Rectangle(
                        bounds=[
                            [result.bounds['min_lat'], result.bounds['min_lon']],
                            [result.bounds['max_lat'], result.bounds['max_lon']]
                        ],
                        color='green',
                        fill=True,
                        fill_opacity=0.2
                    ).add_to(m)
                    
                    st_folium(m, width=400, height=350)
            else:
                st.error(f"❌ Error decoding: {result.error}")
        else:
            st.error(f"❌ **Invalid DIGIPIN:** {message}")
            st.markdown("""
            <div class="result-card error-result">
                <h4 style="margin-top: 0;">💡 Tips</h4>
                <ul>
                    <li>DIGIPIN must be exactly 10 characters</li>
                    <li>Only use valid characters: 2-9, C, F, J, K, L, M, P, T</li>
                    <li>Hyphens are optional (XXX-XXX-XXXX or XXXXXXXXXX)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# TAB 2: ADDRESS TO DIGIPIN
# =============================================================================
with tab2:
    st.markdown("### 📍 Convert Coordinates to DIGIPIN")
    st.markdown("Enter latitude and longitude to generate a DIGIPIN code.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lat_input = st.number_input(
            "Latitude",
            min_value=2.5,
            max_value=38.5,
            value=28.6139,
            step=0.0001,
            format="%.6f",
            help="Valid range: 2.5° to 38.5° (India)"
        )
    
    with col2:
        lon_input = st.number_input(
            "Longitude",
            min_value=63.5,
            max_value=99.5,
            value=77.2090,
            step=0.0001,
            format="%.6f",
            help="Valid range: 63.5° to 99.5° (India)"
        )
    
    # Quick location presets
    st.markdown("**Quick Presets:**")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
    
    presets = {
        "New Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707)
    }
    
    with preset_col1:
        if st.button("🏛️ New Delhi", use_container_width=True):
            st.session_state.lat_preset = 28.6139
            st.session_state.lon_preset = 77.2090
            st.rerun()
    
    with preset_col2:
        if st.button("🌊 Mumbai", use_container_width=True):
            st.session_state.lat_preset = 19.0760
            st.session_state.lon_preset = 72.8777
            st.rerun()
    
    with preset_col3:
        if st.button("🏙️ Bangalore", use_container_width=True):
            st.session_state.lat_preset = 12.9716
            st.session_state.lon_preset = 77.5946
            st.rerun()
    
    with preset_col4:
        if st.button("🌴 Chennai", use_container_width=True):
            st.session_state.lat_preset = 13.0827
            st.session_state.lon_preset = 80.2707
            st.rerun()
    
    convert_btn = st.button("🔄 Convert to DIGIPIN", type="primary", use_container_width=True)
    
    if convert_btn:
        # Check if within India bounds
        if 2.5 <= lat_input <= 38.5 and 63.5 <= lon_input <= 99.5:
            result = validator.encode(lat_input, lon_input)
            
            if result.valid:
                st.markdown("---")
                st.success("✅ **DIGIPIN Generated Successfully!**")
                
                col_result, col_map = st.columns([1, 1])
                
                with col_result:
                    st.markdown(f"""
                    <div class="result-card success-result">
                        <h3 style="margin-top: 0; text-align: center;">🎯 Your DIGIPIN</h3>
                        <div style="text-align: center; padding: 1rem; background: white; border-radius: 8px; margin: 1rem 0;">
                            <h1 style="margin: 0; font-family: monospace; color: #4CAF50;">{result.formatted}</h1>
                        </div>
                        <table style="width: 100%;">
                            <tr><td><strong>Input Coordinates:</strong></td><td>{lat_input:.6f}°, {lon_input:.6f}°</td></tr>
                            <tr><td><strong>Cell Center:</strong></td><td>{result.center_lat:.6f}°, {result.center_lon:.6f}°</td></tr>
                            <tr><td><strong>Resolution:</strong></td><td>~{result.resolution_meters:.1f} meters</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Copy button hint
                    st.code(result.formatted, language=None)
                    st.caption("👆 Click to copy the DIGIPIN code")
                
                with col_map:
                    # Create map
                    m = folium.Map(
                        location=[result.center_lat, result.center_lon],
                        zoom_start=18,
                        tiles="OpenStreetMap"
                    )
                    
                    # Add marker for input location
                    folium.Marker(
                        [lat_input, lon_input],
                        popup=f"Input: {lat_input}, {lon_input}",
                        icon=folium.Icon(color='blue', icon='crosshairs', prefix='fa')
                    ).add_to(m)
                    
                    # Add marker for cell center
                    folium.Marker(
                        [result.center_lat, result.center_lon],
                        popup=f"DIGIPIN: {result.formatted}",
                        icon=folium.Icon(color='green', icon='check')
                    ).add_to(m)
                    
                    # Add rectangle for bounds
                    folium.Rectangle(
                        bounds=[
                            [result.bounds['min_lat'], result.bounds['min_lon']],
                            [result.bounds['max_lat'], result.bounds['max_lon']]
                        ],
                        color='green',
                        fill=True,
                        fill_opacity=0.2
                    ).add_to(m)
                    
                    st_folium(m, width=400, height=350)
            else:
                st.error(f"❌ Error: {result.error}")
        else:
            st.error("❌ Coordinates are outside India's bounds!")
            st.info("Valid range: Latitude 2.5° - 38.5°, Longitude 63.5° - 99.5°")

# =============================================================================
# TAB 3: DIGIPIN TO LOCATION
# =============================================================================
with tab3:
    st.markdown("### 🗺️ DIGIPIN to Location Lookup")
    st.markdown("Enter a DIGIPIN to find its location on the map.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        lookup_digipin = st.text_input(
            "Enter DIGIPIN to Lookup",
            placeholder="e.g., 3PJ-K4M-5L2T",
            max_chars=14,
            key="lookup_digipin"
        )
        
        lookup_btn = st.button("🗺️ Find Location", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; font-size: 0.9em;">
            <strong>🔍 What you'll get:</strong><br>
            • Exact coordinates<br>
            • Map with location<br>
            • Cell boundary area
        </div>
        """, unsafe_allow_html=True)
    
    if lookup_btn and lookup_digipin:
        is_valid, message = validator.validate_with_details(lookup_digipin)
        
        if is_valid:
            result = validator.decode(lookup_digipin)
            
            if result.valid:
                st.markdown("---")
                st.success("✅ **Location Found!**")
                
                # Full width map first
                st.markdown("#### 📍 Location on Map")
                
                # Create map with multiple layers
                m = folium.Map(
                    location=[result.center_lat, result.center_lon],
                    zoom_start=15,
                    tiles=None
                )
                
                # Add multiple tile layers
                folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Satellite'
                ).add_to(m)
                
                # Add marker
                folium.Marker(
                    [result.center_lat, result.center_lon],
                    popup=f"""
                    <b>DIGIPIN:</b> {result.formatted}<br>
                    <b>Lat:</b> {result.center_lat:.6f}°<br>
                    <b>Lon:</b> {result.center_lon:.6f}°
                    """,
                    icon=folium.Icon(color='red', icon='map-marker', prefix='fa')
                ).add_to(m)
                
                # Add rectangle for cell bounds
                folium.Rectangle(
                    bounds=[
                        [result.bounds['min_lat'], result.bounds['min_lon']],
                        [result.bounds['max_lat'], result.bounds['max_lon']]
                    ],
                    color='red',
                    fill=True,
                    fill_opacity=0.3,
                    popup=f"DIGIPIN Cell: {result.formatted}"
                ).add_to(m)
                
                # Add layer control
                folium.LayerControl().add_to(m)
                
                st_folium(m, width=None, height=400, use_container_width=True)
                
                # Details below map
                col_coords, col_bounds = st.columns(2)
                
                with col_coords:
                    st.markdown(f"""
                    <div class="result-card success-result">
                        <h4 style="margin-top: 0;">📍 Coordinates</h4>
                        <table style="width: 100%;">
                            <tr><td><strong>DIGIPIN:</strong></td><td><code>{result.formatted}</code></td></tr>
                            <tr><td><strong>Latitude:</strong></td><td>{result.center_lat:.6f}°</td></tr>
                            <tr><td><strong>Longitude:</strong></td><td>{result.center_lon:.6f}°</td></tr>
                            <tr><td><strong>Resolution:</strong></td><td>~{result.resolution_meters:.1f}m × {result.resolution_meters:.1f}m</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_bounds:
                    st.markdown(f"""
                    <div class="result-card info-result">
                        <h4 style="margin-top: 0;">📐 Cell Boundaries</h4>
                        <table style="width: 100%;">
                            <tr><td><strong>North Edge:</strong></td><td>{result.bounds['max_lat']:.6f}°</td></tr>
                            <tr><td><strong>South Edge:</strong></td><td>{result.bounds['min_lat']:.6f}°</td></tr>
                            <tr><td><strong>East Edge:</strong></td><td>{result.bounds['max_lon']:.6f}°</td></tr>
                            <tr><td><strong>West Edge:</strong></td><td>{result.bounds['min_lon']:.6f}°</td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Google Maps link
                google_maps_url = f"https://www.google.com/maps?q={result.center_lat},{result.center_lon}"
                st.markdown(f"🔗 [Open in Google Maps]({google_maps_url})")
            else:
                st.error(f"❌ Error: {result.error}")
        else:
            st.error(f"❌ **Invalid DIGIPIN:** {message}")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p>🔍 <strong>Public DIGIPIN Services</strong> by AAVA - Authorised Address Validation Agency</p>
    <small>This is a free public service. For address validation services, please contact your local agent.</small>
</div>
""", unsafe_allow_html=True)
