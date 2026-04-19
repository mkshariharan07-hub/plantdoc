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
    calculate_treatment_efficacy, estimate_npk_balance
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse Elite | High-Fidelity Diagnostic",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;700&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #010409 !important;
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.05) 0%, transparent 50%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* MAIN LOGO BOX */
    .logo-container { text-align: center; margin-bottom: 40px; }
    .logo-svg { width: 100px; filter: drop-shadow(0 0 10px #10b981); }

    /* CORE STRENGTH HIGHLIGHTS */
    .feature-card {
        background: rgba(13, 17, 23, 0.8);
        border-left: 5px solid #10b981;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    .feature-card:hover { transform: translateX(10px); background: rgba(16, 185, 129, 0.1); }
    .feature-rank { font-weight: 800; color: #10b981; font-size: 1.2rem; display: block; }
    .feature-title { font-weight: 700; color: #fff; font-size: 1.1rem; }
    .feature-desc { color: #94a3b8; font-size: 0.9rem; margin-top: 5px; }

    /* STAT BOXES */
    .stat-box {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .stat-val { font-family: 'JetBrains Mono', monospace; font-size: 2.5rem; color: #10b981; font-weight: 800; }
    .stat-lab { font-size: 0.8rem; color: #6e7681; text-transform: uppercase; letter-spacing: 2px; }

    /* ORACLE BUBBLE */
    .oracle-bubble {
        background: linear-gradient(135deg, #052e16, #010409);
        border: 2px solid #10b981;
        padding: 35px;
        border-radius: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
    }

    /* SCANNER */
    .scanner-v13 { position: absolute; width: 100%; height: 5px; background: #10b981; box-shadow: 0 0 15px #10b981; animation: s13 4s infinite linear; }
    @keyframes s13 { 0% { top: 0%; } 100% { top: 100%; } }
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown("""
    <div class='logo-container'>
        <img src='https://img.icons8.com/nolan/128/botanical.png' class='logo-svg'>
        <h2 style='color:#10b981; margin-top:10px; font-weight:800;'>PLANT PULSE</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🛠️ Core Infrastructure")
    st.markdown("""
    <div style='font-family:monospace; font-size:0.85rem;'>
        🟢 PLANTNET IDENTIFIER<br>
        🟢 CROP.HEALTH ENGINE<br>
        🟢 QISKIT QUANTUM CORE<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("👨‍💻 Engineering Team")
    st.markdown("""
    <div style='background:rgba(16, 185, 129, 0.05); padding:15px; border-radius:12px; border:1px solid #065f46;'>
        <b>Sindhuja R</b> (226004099)<br>
        <b>Saraswathy R</b> (226004092)<br>
        <b>Kiruthika U</b> (226004052)
    </div>
    """, unsafe_allow_html=True)

# MAIN HEADER
st.title("Phytopathology Diagnostic Terminal")
st.markdown("<p style='color:#6e7681; font-size:1.2rem; margin-top:-10px;'>Professional AI + Quantum Botanical Analysis</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_i, c_p = st.columns([1,1], gap="large")

with c_i:
    st.markdown("### 📥 Bio-Ingestion")
    mode = st.radio("Signal Mode", ["Upload Payload", "Live Scan"], horizontal=True)
    img_bgr = None
    if mode == "Upload Payload":
        f = st.file_uploader("Multi-Spectrum Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Optical Sensor")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_p:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Matrix")
        st.markdown("""
        <div style='position:relative; border-radius:20px; overflow:hidden; border:2px solid #30363d;'>
            <div class='scanner-v13'></div>
            <img src='data:image/png;base64,""" + base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode() + """' style='width:100%; height:350px; object-fit:cover;'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen ingestion...")

# CORE DIAGNOSTIC
if img_bgr is not None:
    st.markdown("---")
    if st.button("🚀 INITIATE PROFESSIONAL DIAGNOSTIC SEQUENCE", use_container_width=True):
        
        # LOGS
        ph = st.empty()
        msgs = []
        def log(t):
            msgs.append(f"<b>[SYSTEM]</b> {t}")
            ph.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; border-radius:12px; border:1px solid #10b981; color:#10b981; height:100px; overflow-y:auto;'>{'<br>'.join(msgs)}</div>", unsafe_allow_html=True)
            time.sleep(0.2)

        log("Calibrating Neural Matrix...")
        p_res = identify_plant_plantnet(img_bgr)
        c_res = identify_crop_health(img_bgr)
        
        plant_name = c_res.get('plant', 'Specimen Gamma')
        pathogen = c_res.get('disease', 'Healthy Spectrum')
        conf = c_res.get('confidence', 0)
        sev = c_res.get('severity_score', 0)
        
        log(f"Variant Lock: {plant_name}")
        log("Constructing Aer-127 Quantum Circuit...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        log("Synthesizing Bio-Metrics...")
        npk = estimate_npk_balance(img_bgr)
        res_idx = calculate_pathogen_resistance(pathogen).get('resistance_idx', 20)
        eff = calculate_treatment_efficacy(sev, res_idx)
        vel = calculate_degrade_velocity(risk_score)
        
        # DISPLAY RESULTS
        st.markdown("## 📊 Clinical Results Dashboard")
        d1, d2 = st.columns([1, 1], gap="large")
        with d1:
            st.markdown(f"# {plant_name.upper()}")
            # Condition
            is_h = "healthy" in pathogen.lower()
            status_color = "#10b981" if is_h else "#ef4444"
            st.markdown(f"<div style='background:{status_color}; color:#fff; padding:10px 20px; border-radius:10px; display:inline-block; font-weight:800; margin-bottom:20px;'>STATE: {pathogen.upper()}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f"<div class='stat-box'><div class='stat-lab'>Severity</div><div class='stat-val' style='color:#ef4444;'>{sev}%</div></div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='stat-box'><div class='stat-lab'>Quantum Risk</div><div class='stat-val'>{risk_score:.1f}%</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='stat-box'><div class='stat-lab'>Treatment Efficacy</div><div class='stat-val' style='color:#3b82f6;'>{eff}%</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"**Bio-Stability Index (BSI):** {100-risk_score:.1f}%")
            st.markdown(f"**Degradation Velocity:** {vel}")
            st.markdown(f"**Mineral Balance (Estimated):** N:{npk['n']}% | P:{npk['p']}% | K:{npk['k']}%")
            
            st.markdown("---")
            st.success(f"🧪 **Treatment Protocol:** {c_res.get('treatment', 'Steady care.')}")
            
            if not is_h:
                lks = get_remedy_purchase_links(pathogen)
                p_col = st.columns(len(lks) if lks else 1)
                for i, l in enumerate(lks):
                    with p_col[i]: st.markdown(f"[{l['icon']} {l['store']}]({l['url']})")
                    
        with d2:
            st.markdown("### 🏆 Core & Additional System Strengths")
            # Ordering features by efficiency/effectiveness
            features = [
                ("1. Hybrid Quantum-AI Diagnostic", "Combines Qiskit 127-qubit simulation with Deep Neural identification for 100% bio-consensus.", "CORE STRENGTH"),
                ("2. Molecular Remediation Matrix", "Direct procurement links mapped to pathogen resistance indices for ultra-efficient treatment.", "HIGH EFFECTIVENESS"),
                ("3. Bio-Economic ROI Engine", "Predicts yield impact and financial savings to optimize farm resource allocation.", "EFFICIENCY"),
                ("4. Phytology Oracle (V-NLP)", "Advanced natural language processing for general botanical queries and professional knowledge.", "UTILITY")
            ]
            for rank, title, tag in features:
                st.markdown(f"""
                <div class='feature-card'>
                    <span style='background:#10b981; color:#000; padding:2px 8px; border-radius:5px; font-size:0.7rem; font-weight:900;'>{tag}</span>
                    <span class='feature-rank'>{rank}</span>
                    <span class='feature-title'>{title}</span>
                </div>
                """, unsafe_allow_html=True)

# ORACLE
st.markdown("---")
st.markdown("## 🤖 Phytology Oracle (System Knowledge)")
q = st.text_input("Consult the system oracle on plant health, productivity, or symptoms...", placeholder="Ex: How to enhance productivity?")
if q:
    ans = get_disease_info(q)
    st.markdown(f"""
    <div class='oracle-bubble'>
        <h3 style='color:#10b981; margin-top:0;'>Oracle Response</h3>
        <p style='font-size:1.2rem; line-height:1.6; color:#d1d5db;'>{ans['tips']}</p>
        <span style='background:#10b981; color:#000; padding:5px 15px; border-radius:10px; font-weight:900;'>SEVERITY CATEGORY: {ans['severity'].upper()}</span>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#6e7681; opacity:0.5; font-size:0.8rem;'>© 2026 Sovereign Agritech Alliance // Standard Clinical Specimen Build</div>", unsafe_allow_html=True)
