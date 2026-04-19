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
    get_live_photoperiod
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantDoc | Zenith Diagnostic",
    page_icon="🔬",
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

    .stat-hero { font-family: 'JetBrains Mono', monospace; font-size: 4rem; font-weight: 900; color: #10b981; }
    .stat-label { font-family: 'Michroma', sans-serif; font-size: 0.7rem; color: #6e7681; text-transform: uppercase; letter-spacing: 3px; }
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
st.markdown("<p class='zen-tag'>ZENITH CLINICAL DIAGNOSTIC SUITE</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c1, c2 = st.columns([1,1], gap="large")

with c1:
    st.markdown("### 📥 Neural Bio-Ingestion")
    f = st.file_uploader("Multispectral Payload", type=["jpg","png","jpeg"])
    img_bgr = None
    if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Zenith Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c2:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Focus (Digital Microscope)")
        h_o, w_o = img_bgr.shape[:2]
        crop = img_bgr[h_o//4:3*h_o//4, w_o//4:3*w_o//4]
        st.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting specimen ingestion for terminal initialization...")

# OVERDRIVE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🎆 INITIATE SUPREME CLINICAL OVERDRIVE", use_container_width=True):
        
        ph = st.empty()
        msgs = []
        def push(t):
            msgs.append(f"<b>[SYSTEM]</b> {t}")
            ph.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; border-radius:12px; border:1px solid #10b981; color:#34d399; height:100px; overflow-y:auto;'>{'<br>'.join(msgs)}</div>", unsafe_allow_html=True)
            time.sleep(0.1)

        push("Initializing Molecular Sync...")
        c_res = identify_crop_health(img_bgr)
        variant = c_res.get('plant', 'Generic Specimen')
        pathogen = c_res.get('disease', 'Healthy Spectrum')
        conf = c_res.get('confidence', 0)
        sev = c_res.get('severity_score', 0)
        rec = c_res.get('recovery_prob', 100)
        
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        n_v = compute_ndvi_score(img_bgr)
        w_v = compute_water_stress_index(img_bgr)
        vel = calculate_degrade_velocity(risk_score)
        
        # DASHBOARD
        st.markdown("## 📊 Ultimate Analytical Report")
        d1, d2 = st.columns([1.2, 0.8], gap="large")
        
        with d1:
            st.markdown("<div class='zen-card'>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='color:#4ade80; margin:0; font-family:Syne; font-size:5rem;'>{variant.upper()}</h1>", unsafe_allow_html=True)
            st.markdown(f"**MOLECULAR STATE:** {'🟢 OPTIMAL' if sev < 20 else '🔴 PATHOGEN DETECTED'}")
            st.markdown(f"**IDENTIFIED PATHOGEN:** <span style='font-size:2rem; font-weight:800; color:#ef4444;'>{pathogen.upper()}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f"<div class='stat-label'>Severity Index</div><div class='stat-hero' style='color:#ef4444;'>{sev}%</div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='stat-label'>Recovery Prob</div><div class='stat-hero' style='color:#4ade80;'>{rec:.0f}%</div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='stat-label'>Quantum Risk</div><div class='stat-hero'>{risk_score:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"**Tissue Degradation Velocity:** {vel}")
            st.markdown(f"**Hydration Potential (WSI):** {100-w_v*100:.1f}%")
            st.markdown(f"**Photosynthetic Capacity (NDVI):** {n_v:.4f}")
            
            st.markdown("---")
            st.markdown(f"<div style='background:#064e3b; padding:30px; border-radius:20px; border:1px solid #10b981;'><b>🧬 ACCURATE CLINICAL REMEDY:</b><br>{c_res.get('treatment')}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, r_lvl, "Treat now.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD COMPREHENSIVE ZENITH REPORT", data=pdf, file_name=f"PlantDoc_Clinical_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            st.markdown("<div class='zen-card' style='padding:40px;'>", unsafe_allow_html=True)
            st.markdown("#### 🌀 Topological Bio-Mesh")
            fig = go.Figure(data=[go.Surface(z=cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100)), colorscale='Greens')])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            st.markdown("#### ⚛️ Molecular Gene Map")
            dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(150)])
            st.markdown(f"<div style='font-family:monospace; color:#10b981; word-break:break-all; background:#000; padding:15px; border-radius:10px; border:1px solid #064e3b;'>{dna}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#6e7681;'>© 2026 Sovereign Biological Collective // PlantDoc v15.0</div>", unsafe_allow_html=True)
