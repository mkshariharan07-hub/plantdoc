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
    decode_bytes_to_bgr
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse AI | Quantum Diagnostics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The Groot Theme)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Nunito', sans-serif !important; }

    .stApp, .main {
        background-color: #1c2b18 !important;
        background-image: 
            radial-gradient(circle at 50% 30%, rgba(206, 230, 94, 0.15) 0%, transparent 60%),
            linear-gradient(180deg, #1f361c 0%, #171d15 100%) !important;
    }

    /* PREMIUM CARD UI */
    .diagnosis-card {
        background: rgba(46, 31, 23, 0.85) !important;
        border: 2px solid #5d4037 !important;
        border-radius: 24px !important;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.4) !important;
        backdrop-filter: blur(8px);
    }

    .status-alert {
        padding: 15px 25px;
        border-radius: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-align: center;
        margin: 15px 0;
    }
    .status-healthy { background: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; color: #10b981; }
    .status-infected { background: rgba(239, 68, 68, 0.2); border: 2px solid #ef4444; color: #ef4444; }

    .metric-box {
        text-align: center;
        padding: 20px;
        background: rgba(0,0,0,0.3);
        border: 1px solid #5d4037;
        border-radius: 15px;
    }
    .metric-box h2 { font-size: 2.8rem !important; margin: 0; color: #b4df41; }
    .metric-box p { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; margin: 0; }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #8bc34a, #689f38) !important;
        color: #111 !important;
        border: 2px solid #aed581 !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        padding: 10px 30px !important;
        text-transform: uppercase;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        transform: scale(1.05) translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(104, 159, 56, 0.6) !important;
    }

    /* GROOT ANIMATIONS */
    @keyframes grootBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .groot-img {
        animation: grootBounce 3s ease-in-out infinite;
        border-radius: 20px;
        border: 4px solid #5d4037;
    }

    @keyframes leafFall {
        0% { transform: translateY(-20px) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
    }
    .magical-leaf {
        position: fixed; top: -5%; z-index: 999; pointer-events: none;
        animation: leafFall 15s linear infinite;
    }
</style>

<div class="magical-leaf" style="left: 10%;">🌿</div>
<div class="magical-leaf" style="left: 30%; animation-delay: 4s;">🍂</div>
<div class="magical-leaf" style="left: 60%; animation-delay: 2s;">🍃</div>
<div class="magical-leaf" style="left: 85%; animation-delay: 7s;">🌱</div>
""", unsafe_allow_html=True)

# ===============================
# ASSETS & HELPERS
# ===============================
@st.cache_resource
def load_assets():
    return load_model_and_scaler()

model, scaler = load_assets()

def decode_image(source):
    if source is None: return None
    try:
        return decode_bytes_to_bgr(source.getvalue())
    except: return None

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("<img src='https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif' class='groot-img' width='100%'>", unsafe_allow_html=True)
    st.title("I AM GROOT")
    st.caption("Botanical AI v5.0 // Quantum Pipeline")
    st.markdown("---")
    
    st.subheader("👨‍💻 Project Team")
    st.info("**Sindhuja R** (226004099)\n\n**Saraswathy R** (226004092)\n\n**U. Kiruthika** (226004052)")
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    st.success("Quantum Core: ONLINE")
    st.success("PlantNet API: LINKED")
    st.success("CropHealth: ACTIVE")

# ===============================
# MAIN UI
# ===============================
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <h1 style='color: #b4df41; font-size: 4rem; margin-bottom: 0;'>PlantPulse</h1>
    <p style='color: #94a3b8; font-size: 1.2rem;'>Hybrid AI + Quantum Expert Diagnostic System</p>
</div>
""", unsafe_allow_html=True)

# SPECIMEN INPUT
col_input, col_display = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 📥 Specimen Ingestion")
    source_tab = st.radio("Choose Input Mode:", ["📁 File Upload", "📷 Live Camera"], horizontal=True)
    
    specimen = None
    if source_tab == "📁 File Upload":
        uploaded = st.file_uploader("Drop leaf specimen here", type=["jpg", "png", "jpeg"])
        if uploaded: specimen = decode_image(uploaded)
    else:
        captured = st.camera_input("Scan specimen directly")
        if captured: specimen = decode_image(captured)

with col_display:
    if specimen is not None:
        st.markdown("### 🍃 Specimen Preview")
        st.image(cv2.cvtColor(specimen, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Active Specimen for Analysis")
    else:
        st.markdown("""
        <div style='height: 300px; display: flex; align-items: center; justify-content: center; border: 2px dashed #5d4037; border-radius: 20px;'>
            <p style='color: #475569;'>Awaiting specimen for terminal analysis...</p>
        </div>
        """, unsafe_allow_html=True)

# ANALYSIS TRIGGER
if specimen is not None:
    st.markdown("---")
    if st.button("🚀 INITIATE SCAN & QUANTUM ANALYSIS", use_container_width=True, type="primary"):
        
        # 1. SCANNING ENGINE
        with st.status("📡 Initializing Botanical Frequency Scan...", expanded=True) as status:
            
            # --- STEP 1: PLANT IDENTIFICATION ---
            st.write("🔍 Identifying plant variant via PlantNet matrix...")
            p_res = identify_plant_plantnet(specimen)
            variant = p_res.get('plant', 'Unknown')
            scientific = p_res.get('scientific_name', 'N/A')
            
            # --- STEP 2: DISEASE STATUS ---
            st.write("🧬 Analyzing cellular integrity via Crop.Health...")
            c_res = identify_crop_health(specimen)
            disease_name = c_res.get('disease', 'Healthy')
            d_conf = c_res.get('confidence', 0.0)
            is_diseased = "healthy" not in disease_name.lower()
            
            # Update Status
            status.update(label=f"Scan Complete: {variant} detected.", state="complete")

        # --- RESULTS PRESENTATION ---
        st.markdown(f"<div class='diagnosis-card'>", unsafe_allow_html=True)
        
        # Heading: Plant Name
        st.markdown(f"<h2 style='color: #b4df41; text-align: center;'>IDENTIFIED: {variant}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #94a3b8; font-style: italic;'>Species: {scientific}</p>", unsafe_allow_html=True)
        
        # Disease Status Banner
        if is_diseased:
            st.markdown(f"<div class='status-alert status-infected'>🦠 PATHOGEN DETECTED: {disease_name.upper()}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-alert status-healthy'>✨ STATE: HEALTHY SPECIMEN</div>", unsafe_allow_html=True)

        if is_diseased:
            # --- QUANTUM ANALYSIS ---
            with st.spinner("⚛️ Running Quantum Entropy Analysis (Qiskit)..."):
                qc, entropy = build_quantum_circuit(specimen)
                q_res, backend_name = run_quantum(qc)
                risk_score, risk_level = calculate_quantum_risk(q_res, entropy)
            
            st.markdown("### ⚛️ Quantum Risk Intelligence")
            q_col1, q_col2, q_col3 = st.columns(3)
            with q_col1:
                st.markdown("<div class='metric-box'><p>Risk Level</p><h2 style='color: #ef4444;'>"+risk_level+"</h2></div>", unsafe_allow_html=True)
            with q_col2:
                st.markdown("<div class='metric-box'><p>Entropy Core</p><h2>"+str(risk_score)+"%</h2></div>", unsafe_allow_html=True)
            with q_col3:
                st.markdown("<div class='metric-box'><p>Backend</p><h4 style='color: #34d399;'>"+backend_name+"</h4></div>", unsafe_allow_html=True)
            
            # --- REMEDIES & INFO ---
            st.markdown("---")
            st.markdown("### 💊 Expert Remediation Protocol")
            treatment = c_res.get('treatment', "Consult an agricultural expert for specific treatment.")
            st.success(f"**Primary Action:** {treatment}")
            
            # Additional Info
            care_data = get_perenual_care_info(variant)
            
            info_tab1, info_tab2 = st.tabs(["📋 Detailed Report", "🔍 Biological Metrics"])
            with info_tab1:
                st.markdown("**Pathogen Profile:** " + disease_name)
                st.markdown("**Survival Forecast:** 30-Day risk projection indicates " + ("HIGH" if risk_score > 50 else "MODERATE") + " volatility.")
                if care_data and "error" not in care_data:
                    st.write("---")
                    st.write("**Botanical Care Requirements:**")
                    st.write(f"- Watering: {care_data.get('watering', 'Regular')}")
                    st.write(f"- Sunlight: {', '.join(care_data.get('sunlight', ['Full Sun']))}")
            
            with info_tab2:
                # Textures for report
                gray = cv2.cvtColor(specimen, cv2.COLOR_BGR2GRAY)
                std_dev = np.std(gray)
                texture_data = {
                    "texture_index": round(std_dev / 25.5, 2),
                    "classification": "Granular" if std_dev > 40 else "Smooth",
                    "edge_density": round(float(np.sum(cv2.Canny(gray, 50, 150) > 0)) / gray.size * 100, 2)
                }
                st.write(f"- Texture Index: {texture_data['texture_index']} ({texture_data['classification']})")
                st.write(f"- Cell Edge Density: {texture_data['edge_density']}%")
                
            # --- FINAL REPORT DOWNLOAD ---
            st.markdown("---")
            leaf_health = max(0, 100 - risk_score)
            mask = generate_pathogen_mask(specimen)
            necrotic_ratio = round(float(np.sum(mask > 0)) / mask.size * 100, 2)
            
            pdf_bytes = generate_pdf_report(
                variant, disease_name, d_conf, risk_level, treatment, 
                risk_score, leaf_health, care_data, necrotic_ratio, texture_data
            )
            
            st.download_button(
                label="📥 DOWNLOAD QUANTUM CLINICAL DOSSIER",
                data=pdf_bytes,
                file_name=f"PlantPulse_Report_{variant}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        else:
            # Healthy specimen additional info
            st.markdown("### ✨ Health Report")
            st.write(f"The {variant} specimen shows optimal cellular structure. No pathogens detected within the current matrix depth.")
            st.info("💡 **Maintenance Tip:** Continue standard watering and nutrient regimes. Monitor for local environmental changes.")
            
            care_data = get_perenual_care_info(variant)
            if care_data and "error" not in care_data:
                with st.expander("🌿 View Optimal Care Guide for Healthy Growth"):
                    st.write(f"**Preferred Cycle:** {care_data.get('cycle', 'Perennial')}")
                    st.write(f"**Watering Needs:** {care_data.get('watering', 'Standard')}")

        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 20px; border-top: 1px solid rgba(180, 223, 65, 0.2);'>
    <p style='color: #475569; font-size: 0.8rem; font-family: monospace;'>
        PLANT PULSE TECHNOLOGIES © 2026<br>
        v5.0 Enterprise Hybrid Quantum-Classical Engine<br>
        Sindhuja · Saraswathy · Kiruthika
    </p>
</div>
""", unsafe_allow_html=True)
