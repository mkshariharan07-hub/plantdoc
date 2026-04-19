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
import hashlib
import sqlite3
import time
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Shared Utilities
from utils import (
    identify_plant_plantnet, identify_crop_health, get_disease_info,
    predict_image, load_model_and_scaler, build_quantum_circuit,
    run_quantum, calculate_quantum_risk, generate_pdf_report,
    get_perenual_care_info, generate_pathogen_mask,
    decode_bytes_to_bgr, compute_leaf_texture_score, 
    compute_ndvi_score, compute_water_stress_index, 
    estimate_nitrogen_content, calculate_yield_impact,
    calculate_pathogen_resistance, calculate_farm_roi,
    estimate_biological_age, get_remedy_purchase_links,
    classify_pathogen_severity, calculate_global_rank,
    generate_growth_forecast, calculate_molecular_stress_index,
    predict_harvest_revenue, calculate_degrade_velocity,
    calculate_treatment_efficacy, estimate_npk_balance,
    get_live_photoperiod, estimate_carbon_sequestration,
    get_health_gauge_color
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantDoc | Zenith Supreme",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# ZENITH STYLE
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&family=Michroma&family=Space+Grotesk:wght@300;700&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }
    .stApp { background: #010204 !important; }
    
    .zen-title { font-family: 'Syne', sans-serif; font-size: 8rem; font-weight: 800; color: #4ade80; text-align: center; margin: 0; letter-spacing: -8px; }
    .zen-tag { font-family: 'Michroma', sans-serif; font-size: 0.9rem; color: #10b981; text-align: center; letter-spacing: 12px; margin-top: 10px; }

    .zen-card {
        background: rgba(13, 17, 23, 0.9) !important;
        border: 2px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 40px !important;
        padding: 50px;
        backdrop-filter: blur(50px);
        box-shadow: 0 50px 150px -30px rgba(0, 0, 0, 1);
        margin-bottom: 50px;
    }

    .hero-metric { text-align: center; padding: 20px; border-radius: 24px; background: rgba(0,0,0,0.5); border: 1px solid #14532d; }
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.markdown("### 📡 ENVIRONMENTAL TELEMETRY")
    p = get_live_photoperiod()
    st.markdown(f"""
    <div style='background:rgba(16,185,129,0.1); padding:15px; border-radius:15px; border:1px solid #10b981;'>
        <b>DAY LENGTH:</b> {p.get('day_length', '12:00:00')}<br>
        <b>SUNRISE:</b> {p.get('sunrise', '06:00:00')}<br>
        <b>SUNSET:</b> {p.get('sunset', '18:00:00')}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 👨‍💻 CHIEF ARCHITECTS")
    st.markdown("<div style='color:#10b981;'>Sindhuja R | Saraswathy R | Kiruthika U</div>", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 class='zen-title'>PlantDoc</h1>", unsafe_allow_html=True)
st.markdown("<p class='zen-tag'>SUPREME CLINICAL BIO-INTERFACE // v16.0</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c1, c2 = st.columns([1,1], gap="large")

with c1:
    st.markdown("### 📥 Bio-Ingestion")
    f = st.file_uploader("Select Multispectral Payload", type=["jpg","png","jpeg"])
    img_bgr = None
    if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Zenith Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c2:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Focus")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting specimen ingestion...")

# OVERDRIVE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE SUPREME CLINICAL OVERDRIVE", use_container_width=True):
        
        ph = st.empty()
        m = []
        def push(t):
            m.append(f"<b>[SYSTEM]</b> {t}")
            ph.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; border-radius:12px; border:1px solid #10b981; color:#34d399; height:100px; overflow-y:auto;'>{'<br>'.join(m)}</div>", unsafe_allow_html=True)
            time.sleep(0.1)

        push("Initializing Molecular Sync...")
        c_res = identify_crop_health(img_bgr)
        variant = c_res.get('plant', 'Generic Specimen')
        pathogen = c_res.get('disease', 'Healthy Spectrum')
        conf = c_res.get('confidence', 0)
        sev = c_res.get('severity_score', 0)
        rec = c_res.get('recovery_prob', 100)
        
        push("Calibrating Aer-127 Quantum Backend...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        push("Synthesizing Biometric Data...")
        n_v = compute_ndvi_score(img_bgr)
        w_v = compute_water_stress_index(img_bgr)
        age = estimate_biological_age(img_bgr)
        carbon = estimate_carbon_sequestration(n_v, age)
        mask = generate_pathogen_mask(img_bgr)
        
        # DASHBOARD
        st.markdown("## 📊 Clinical Zenith Dashboard")
        d1, d2 = st.columns([1, 1], gap="large")
        
        with d1:
            st.markdown("<div class='zen-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#4ade80; margin:0; font-family:Syne; font-size:4.5rem;'>{variant.upper()}</h1>", unsafe_allow_html=True)
            is_h = "healthy" in pathogen.lower()
            st.markdown(f"**MOLECULAR STATE:** {'🟢 OPTIMAL' if is_h else '🔴 ' + pathogen.upper()}")
            
            # GAUGE
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 100 - sev,
                title = {'text': "Bio-Stability Index"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': get_health_gauge_color(sev)},
                    'steps': [{'range': [0, 50], 'color': "rgba(239,68,68,0.2)"}, {'range': [50, 100], 'color': "rgba(16,185,129,0.2)"}]}
            ))
            fig.update_layout(height=250, margin=dict(l=20,r=20,t=50,b=0), paper_bgcolor="rgba(0,0,0,0)", font_color="#10b981")
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.markdown(f"### 🧬 ACCURATE CLINICAL REMEDY:")
            st.markdown(f"<div style='background:#064e3b; padding:25px; border-radius:20px; border:1px solid #10b981;'>{c_res.get('treatment')}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            k1, k2 = st.columns(2)
            with k1: st.metric("Carbon Sequestration", f"{carbon} gCO2/day")
            with k2: st.metric("Biological Age", f"{age} Days")
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, r_lvl, "Treat now.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD SUPREME CLINICAL DOSSIER", data=pdf, file_name=f"PlantDoc_Supreme_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            st.markdown("<div class='zen-card' style='padding:40px;'>", unsafe_allow_html=True)
            t1, t2, t3 = st.tabs(["🌀 Pathogen Heatmap", "📈 Growth Forecast", "⚛️ DNA Space"])
            with t1:
                st.markdown("#### Pathogen Saturation Heatmap")
                try:
                    # Blend mask with image
                    overlay = cv2.addWeighted(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), 0.7, cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB), 0.3, 0)
                    st.image(overlay, use_container_width=True, caption="Neon highlights represent cellular degradation zones.")
                except: st.write("Generating heatmap...")
            with t2:
                st.markdown("#### 7-Day Biomass Accumulation")
                st.line_chart(generate_growth_forecast(n_v))
            with t3:
                dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(200)])
                st.markdown(f"<div style='font-family:monospace; color:#10b981; word-break:break-all; background:#000; padding:15px;'>{dna}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#6e7681;'>© 2026 Sovereign Biological Collective // PlantDoc v16.0</div>", unsafe_allow_html=True)
