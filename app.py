import streamlit as st
import cv2
import numpy as np
import os
import requests
import json
import base64
import datetime
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Shared Utilities
from utils import (
    identify_plant_plantnet, identify_crop_health, get_disease_info,
    predict_image, load_model_and_scaler, build_quantum_circuit,
    run_quantum, calculate_quantum_risk, generate_pdf_report,
    simulate_environment, get_perenual_care_info, generate_pathogen_mask,
    decode_bytes_to_bgr, compute_leaf_texture_score
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse Pro | Enterprise Ag-Tech",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (Ultimate Groot UI)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }

    .stApp, .main {
        background-color: #1c2b18 !important;
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(206, 230, 94, 0.15) 0%, transparent 60%),
            linear-gradient(180deg, #1f361c 0%, #171d15 100%) !important;
    }

    /* GLASSMORPHISM UI */
    .glass-panel {
        background: rgba(46, 31, 23, 0.7) !important;
        border: 1px solid rgba(180, 223, 65, 0.2) !important;
        border-radius: 20px !important;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* PREMIUM METRICS */
    .metric-card {
        background: rgba(0, 0, 0, 0.4);
        border-left: 5px solid #b4df41;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; color: #b4df41; weight: 900; }
    .metric-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }

    /* STATUS COMPONENTS */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 8px;
    }
    .badge-high { background: #ef4444; color: white; }
    .badge-mid { background: #f59e0b; color: white; }
    .badge-safe { background: #10b981; color: white; }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #8bc34a, #689f38) !important;
        color: #111 !important;
        border: 2px solid #aed581 !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(104, 159, 56, 0.4) !important;
    }

    /* ANIMATIONS */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(180, 223, 65, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(180, 223, 65, 0); }
        100% { box-shadow: 0 0 0 0 rgba(180, 223, 65, 0); }
    }
    .scanning-active {
        animation: pulse-green 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# ASSETS & HELPERS
# ===============================
@st.cache_resource
def load_assets():
    return load_model_and_scaler()

model, scaler = load_assets()

def decode_image_enhanced(file):
    if file is None: return None
    try:
        arr = np.asarray(bytearray(file.read()), dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except: return None

# ===============================
# SIDEBAR — CONTROL CENTER
# ===============================
with st.sidebar:
    st.markdown("<img src='https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif' style='border-radius:15px; border:2px solid #b4df41; width:100%'>", unsafe_allow_html=True)
    st.title("PlantPulse Pro")
    st.caption("v5.1 Enterprise Suite // Global Ag-Monitoring")
    
    st.markdown("---")
    st.subheader("📡 IoT Link Status")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Node A: ✅")
        st.write("Node B: ✅")
    with col2:
        st.write("Drone 1: 🛸")
        st.write("Orbit: 🛰️")
        
    st.markdown("---")
    st.subheader("🧪 Live Lab Mode")
    lab_mode = st.toggle("Enable Advanced CV Metrics", value=True)
    quantum_boost = st.toggle("Quantum Depth Enhancement", value=True)
    
    st.markdown("---")
    with st.expander("👤 Contact Support"):
        st.write("**Sindhuja R**\nReg No: 226004099")
        st.write("**Saraswathy R**\nReg No: 226004092")
        st.write("**U. Kiruthika**\nReg No: 226004052")

# ===============================
# MAIN UI — DASHBOARD
# ===============================
# Header with Ticker
st.markdown("""
<div style="background: #020617; padding: 10px; margin-bottom: 20px; border: 1px solid #1e293b; border-radius: 8px;">
    <marquee scrollamount="5" style="color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
        [GLOBAL TICKER] &nbsp;&nbsp; 🌽 CORN: $4.50 (▲ 0.8%) &nbsp;&nbsp;█&nbsp;&nbsp; 🌱 SOY: $12.44 (▼ 0.2%) &nbsp;&nbsp;█&nbsp;&nbsp; 🌾 WHEAT: $6.12 (▼ 0.4%) &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ ORBITAL TELEMETRY: NOMINAL &nbsp;&nbsp;█&nbsp;&nbsp; ⚛️ QUANTUM SYNC: ACTIVE &nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# INGESTION LAYER
st.markdown("## 📥 Specimen Ingestion Layer")
tab_ingest, tab_batch = st.tabs(["🎯 Precision Ingestion", "📦 Batch Processing (New)"])

specimens = []

with tab_ingest:
    ingest_c1, ingest_c2 = st.columns([1, 1])
    with ingest_c1:
        input_mode = st.segmented_control("Input Source", ["Upload", "Camera"], selection_mode="single", default="Upload")
        if input_mode == "Upload":
            single_file = st.file_uploader("Upload leaf specimen", type=["jpg","png","jpeg"], label_visibility="collapsed")
            if single_file: specimens.append(decode_image_enhanced(single_file))
        else:
            cam_file = st.camera_input("Capture live specimen", label_visibility="collapsed")
            if cam_file: specimens.append(decode_image_enhanced(cam_file))
    with ingest_c2:
        if specimens:
            st.image(cv2.cvtColor(specimens[0], cv2.COLOR_BGR2RGB), use_container_width=True, caption="Active Precision Specimen")
        else:
            st.info("Awaiting specimen ingestion for terminal mapping.")

with tab_batch:
    batch_files = st.file_uploader("Upload multiple specimens for batch analysis", type=["jpg","png","jpeg"], accept_multiple_files=True)
    if batch_files:
        st.success(f"{len(batch_files)} specimens added to queue.")
        for f in batch_files: specimens.append(decode_image_enhanced(f))

# ANALYSIS ENGINE
if specimens:
    st.markdown("---")
    st.markdown("## ⚙️ Hybrid Expert Pipeline")
    
    if st.button("🚀 EXECUTE FULL ANALYTICAL SEQUENCE", use_container_width=True):
        
        for idx, img in enumerate(specimens):
            if img is None: continue
            
            with st.status(f"🛠️ Processing Specimen {idx+1}/{len(specimens)}...", expanded=True) as status:
                
                # --- PIEPLINE EXECUTION ---
                p_res = identify_plant_plantnet(img)
                c_res = identify_crop_health(img)
                variant = p_res.get('plant', 'Unknown')
                disease = c_res.get('disease', 'Healthy')
                is_diseased = "healthy" not in disease.lower()
                
                status.write(f"✅ Ident Mapping: **{variant}**")
                status.write(f"✅ Pathogen Scan: **{disease}**")
                
                # QUANTUM
                qc, entropy = build_quantum_circuit(img)
                q_res, backend = run_quantum(qc)
                score, level = calculate_quantum_risk(q_res, entropy)
                status.write(f"✅ Quantum Consensus: **{level}**")
                
                status.update(label=f"Specimen {idx+1} Fully Analyzed", state="complete")

            # --- PRESENTATION LAYER ---
            st.markdown(f"### 📋 Analysis Report: {variant}")
            
            res_c1, res_c2 = st.columns([2, 3])
            
            # Left: Main Metrics
            with res_c1:
                st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
                st.markdown(f"**State:** {'🔴 INFECTED' if is_diseased else '🟢 HEALTHY'}")
                st.markdown(f"**Pathogen:** {disease}")
                
                # Metric Cards
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<div class='metric-card'><span class='metric-label'>AI Conf</span><div class='metric-value'>{c_res.get('confidence', 0)}%</div></div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-card'><span class='metric-label'>Q-Risk</span><div class='metric-value' style='color:#ef4444'>{score}%</div></div>", unsafe_allow_html=True)
                
                st.markdown(f"**Remediation:** {c_res.get('treatment', 'N/A')}")
                st.markdown("</div>", unsafe_allow_html=True)

            # Right: Advanced Features
            with res_c2:
                feat_tabs = st.tabs(["⚛️ Quantum Report", "🌡️ IoT Sensors", "🗺️ Threat Radar", "🌀 3D Topology"])
                
                with feat_tabs[0]:
                    st.markdown("#### Quantum Entropy Matrix")
                    st.write(f"Executed on: `{backend}`")
                    st.caption("Subatomic breakdown of tissue stability. High entropy suggests cellular necrosis spread.")
                    # Quantum Chart
                    fig_q = go.Figure(go.Indicator(
                        mode = "gauge+number", value = score,
                        title = {'text': "Entropy Deviation"},
                        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#ef4444"}}
                    ))
                    fig_q.update_layout(height=250, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                    st.plotly_chart(fig_q, use_container_width=True)

                with feat_tabs[1]:
                    st.markdown("#### Simulated IoT Sensor Mesh")
                    st.caption("Simulating real-time data from Node Alpha-7 (Field Proximity).")
                    env = simulate_environment()
                    col_env1, col_env2 = st.columns(2)
                    col_env1.metric("Ambient Temp", f"{env['temp']}°C", "+1.2%")
                    col_env1.metric("UV Index", f"{env['uv_index']} U", "-0.1")
                    col_env2.metric("Soil Humidity", f"{env['humidity']}%", "-4.5%")
                    col_env2.metric("Capillary H2O", f"{env['soil_moisture']}%", "+0.8%")

                with feat_tabs[2]:
                    st.markdown("#### Regional Outbreak Radar")
                    st.caption("Synthetic satellite telemetry mapping nearby pathogen clusters.")
                    map_data = pd.DataFrame(np.random.randn(50, 2) / [20, 20] + [37.77, -122.42], columns=['lat', 'lon'])
                    st.pydeck_chart(pdk.Deck(
                        map_style='mapbox://styles/mapbox/dark-v11',
                        initial_view_state=pdk.ViewState(latitude=37.77, longitude=-122.42, zoom=10, pitch=45),
                        layers=[pdk.Layer('HexagonLayer', data=map_data, get_position='[lon, lat]', radius=200, extruded=True, pickable=True, elevation_scale=4, elevation_range=[0, 1000])]
                    ))

                with feat_tabs[3]:
                    st.markdown("#### 3D Tissue Surface Topography")
                    st.caption("Interactive 3D reconstruction based on grayscale luminosity mapping (Z-Axis = Tissue Density).")
                    img_small = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (100, 100))
                    fig_3d = go.Figure(data=[go.Surface(z=img_small, colorscale='Viridis')])
                    fig_3d.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False)), height=350, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_3d, use_container_width=True)

            # Download Option
            st.markdown("---")
            mask = generate_pathogen_mask(img)
            n_ratio = round(float(np.sum(mask > 0)) / mask.size * 100, 2)
            texture = compute_leaf_texture_score(img)
            care = get_perenual_care_info(variant)
            
            pdf_bytes = generate_pdf_report(
                variant, disease, c_res.get('confidence',0), level, 
                c_res.get('treatment',''), score, max(0, 100-score), care, n_ratio, texture
            )
            st.download_button(f"📥 Download Clinical Dossier for {variant}", data=pdf_bytes, file_name=f"PlantPulse_Report_{variant}.pdf", mime="application/pdf")
            st.markdown("<br>", unsafe_allow_html=True)

# METEOROLOGICAL THREAT CALCULATOR (Global Feature)
st.markdown("---")
st.markdown("## 🌦️ Meteorological Impact Forecast")
st.caption("Adjust environmental parameters to predict disease transmission velocity.")
met_c1, met_c2 = st.columns([2, 1])
with met_c1:
    m_temp = st.slider("Ambient Temperature (°C)", 10, 45, 24)
    m_hum = st.slider("Relative Humidity (%)", 0, 100, 65)
    
    # Simple risk model
    spread_risk = "Low"
    s_color = "#10b981"
    if m_hum > 80 and m_temp > 25:
        spread_risk, s_color = "Critical", "#ef4444"
    elif m_hum > 60:
        spread_risk, s_color = "Elevated", "#f59e0b"
        
    st.markdown(f"""
    <div style='background: {s_color}22; border: 2px solid {s_color}; border-radius: 15px; padding: 20px; text-align: center;'>
        <h3 style='color: {s_color}; margin: 0;'>{spread_risk} TRANSMISSION RISK</h3>
        <p style='color: #94a3b8; font-family: monospace; font-size: 0.9rem;'>Atmospheric suitability index for fungal spore germination.</p>
    </div>
    """, unsafe_allow_html=True)
with met_c2:
    st.markdown("#### 🤖 Ask Dr. Leaf (Expert System)")
    user_q = st.text_input("Query the botanical database...", placeholder="How do I cure Leaf Mold?")
    if user_q:
        # Simple local search logic
        d_info = get_disease_info(user_q)
        st.success(f"**Dr. Leaf Says:** \n\n {d_info['tips']}")

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #475569; font-size: 0.8rem; border-top: 1px solid rgba(180, 223, 65, 0.1); padding-top: 20px;'>
    PLANT PULSE TECHNOLOGIES INC. — ENTERPRISE EDITION<br>
    Built with Python, Streamlit, Qiskit & OpenCV<br>
    © 2026 Global Agricultural Intelligence Network
</div>
""", unsafe_allow_html=True)
