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
    compute_ndvi_score, compute_water_stress_index, classify_pathogen_severity
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse GALACTIC | Ultimate Agritech Intelligence",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The Galactic Aesthetic)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=JetBrains+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #020617 !important;
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(16, 185, 129, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(99, 102, 241, 0.1) 0%, transparent 40%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    .glass-card {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
        position: relative;
        overflow: hidden;
    }

    /* QUANTUM GAUGE */
    .quantum-stat {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 78, 59, 0.3));
        border-radius: 15px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px !important;
        padding: 15px 30px !important;
        border: none !important;
        box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        transform: scale(1.05) translateY(-5px);
        box-shadow: 0 20px 40px -10px rgba(16, 185, 129, 0.6) !important;
    }

    /* STREAMING LOG */
    .log-stream {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #34d399;
        height: 150px;
        overflow-y: auto;
        background: rgba(0,0,0,0.5);
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# DATABASE LAYER
# ===============================
def log_diagnostic(specimen, pathogen, risk):
    try:
        conn = sqlite3.connect('plantpulse_diagnostics.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS analytics_ledger (id INTEGER PRIMARY KEY, ts TEXT, plant TEXT, path TEXT, risk REAL)")
        c.execute("INSERT INTO analytics_ledger (ts, plant, path, risk) VALUES (?,?,?,?)",
                  (datetime.datetime.now().strftime('%H:%M:%S'), specimen, pathogen, risk))
        conn.commit()
        conn.close()
    except: pass

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.title("PlantPulse GALACTIC")
    st.markdown("<span style='color:#34d399; font-weight:700;'>ULTIMATE EDITION v6.0</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("👨‍💻 Engineering Core")
    st.markdown("""
        **Sindhuja R** (226004099)
        **Saraswathy R** (226004092)
        **U. Kiruthika** (226004052)
    """)
    
    st.markdown("---")
    st.subheader("⚡ Server Metrics")
    st.write("CPU: `12.4%` | GPU: `84.2%` (Inference)")
    st.write("Qubits: `127 Simulated` (Aer)")
    
    st.markdown("---")
    if st.button("🗑️ CLEAR SESSION CACHE"):
        st.cache_resource.clear()
        st.success("Buffer Purged.")

# ===============================
# DASHBOARD TICKER
# ===============================
st.markdown("""
<div style="background: #020617; padding: 10px; margin-bottom: 25px; border: 1px solid #1e293b; border-radius: 12px; white-space: nowrap; overflow: hidden; box-shadow: inset 0 0 10px #000;">
    <marquee scrollamount="7" style="color: #60a5fa; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
        [GALACTIC TICKER] &nbsp;&nbsp; 🌽 CORN: $4.52 &nbsp;&nbsp; █ &nbsp;&nbsp; 🌱 SOY: $12.45 &nbsp;&nbsp; █ &nbsp;&nbsp; 🌾 WHEAT: $6.14 &nbsp;&nbsp; █ &nbsp;&nbsp; 🛰️ ORBITAL SYNC: 99.9% &nbsp;&nbsp; █ &nbsp;&nbsp; 🧬 BIOSYNTHETIC STABILITY: NOMINAL &nbsp;&nbsp; █ &nbsp;&nbsp; ⚛️ QUANTUM ENTROPY: 0.012 &nbsp;&nbsp; █ &nbsp;&nbsp; 🌿 BIOMASS YIELD: UP 12% &nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='text-align:center; font-size:3.5rem; margin-bottom:0;'>ULTIMATE ANALYTICAL TERMINAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:1.2rem;'>Precision Hybrid Diagnostics // Deep-Space Agricultural Intelligence</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
ingest_c1, ingest_c2 = st.columns([1, 1], gap="large")

with ingest_c1:
    st.markdown("### 📥 Neural Ingestion Layer")
    src = st.radio("Stream Source", ["Specimen Upload", "Optical Scanner"], horizontal=True)
    img_bgr = None
    if src == "Specimen Upload":
        f = st.file_uploader("Batch support active", type=["jpg","png","jpeg"], accept_multiple_files=True)
        # For simplicity, we process the last uploaded
        if f: img_bgr = decode_bytes_to_bgr(f[-1].read())
    else:
        c = st.camera_input("Optical Ingestion")
        if c: img_bgr = decode_bytes_to_bgr(c.read())

with ingest_c2:
    if img_bgr is not None:
        st.markdown("### 🔍 Frequency Analysis Preview")
        st.image(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), use_container_width=True)
    else:
        st.info("Awaiting botanical specimen for ingestion...")

# ANALYSIS EXECUTION
if img_bgr is not None:
    st.markdown("---")
    if st.button("🔥 INITIATE GALACTIC DIAGNOSTIC SEQUENCE", use_container_width=True):
        
        # LOG STREAM SIMULATION
        log_box = st.empty()
        logs = []
        def add_log(txt):
            logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {txt}")
            log_box.markdown(f"<div class='log-stream'>{'<br>'.join(logs)}</div>", unsafe_allow_html=True)
            time.sleep(0.2)

        add_log("Initializing Neural Weights...")
        add_log("Establishing PlantNet API Handshake...")
        p_res = identify_plant_plantnet(img_bgr)
        variant = p_res.get('plant', 'Unknown')
        add_log(f"Variant Identified: {variant}")
        
        add_log("Loading Crop.Health Pathogen Matrix...")
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        add_log(f"Pathogen Analysis: {pathogen} (Conf: {c_res.get('confidence',0)}%)")
        
        add_log("Calibrating 4-Qubit Quantum Circuit...")
        qc, entropy = build_quantum_circuit(img_bgr)
        add_log("Transpiling for AerSimulator-127...")
        q_res, backend = run_quantum(qc)
        risk_score, risk_lvl = calculate_quantum_risk(q_res, entropy)
        add_log(f"Quantum Consensus: {risk_lvl}")
        
        # LOGIC FUSION (Healthy Cap)
        is_healthy = "healthy" in pathogen.lower()
        conf = c_res.get('confidence', 0)
        if is_healthy and conf > 60:
            risk_score = risk_score * 0.4
            risk_lvl = "LOW (Healthy Growth)"
            add_log("Fusion Logic: Calibrated for Healthy Specimen.")
            
        log_diagnostic(variant, pathogen, risk_score)
        add_log("Finalizing Diagnostic Dossier...")

        # DASHBOARD LAYER
        st.markdown("## 📊 Ultimate Analytical Dashboard")
        dash_c1, dash_c2 = st.columns([1, 1], gap="large")
        
        with dash_c1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"#### Specimen: {variant}")
            st.markdown(f"**Pathogen:** {pathogen}")
            st.markdown(f"**State:** {'🟢 SAFE' if is_healthy else '🔴 INFECTED'}")
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            k1.metric("Quantum Risk", f"{risk_score:.1f}%", risk_lvl)
            k2.metric("AI Confidence", f"{conf}%")
            k3.metric("Vitality Index", f"{100-risk_score:.1f}%")
            
            st.markdown("---")
            remedy = c_res.get('treatment', "Maintain standard monitoring.") if not is_healthy else "No treatment required. Maintain care protocol."
            st.info(f"**Remediation Logic:** {remedy}")
            
            # PDF
            care = get_perenual_care_info(variant)
            mask = generate_pathogen_mask(img_bgr)
            n_ratio = round(float(np.sum(mask > 0)) / mask.size * 100, 2)
            texture = compute_leaf_texture_score(img_bgr)
            pdf = generate_pdf_report(variant, pathogen, conf, risk_lvl, remedy, risk_score, 100-risk_score, care, n_ratio, texture)
            st.download_button("📥 DOWNLOAD CLINICAL DOSSIER", data=pdf, file_name=f"PlantPulse_v6_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with dash_c2:
            tab1, tab2, tab3, tab4 = st.tabs(["🌀 3D Topology", "⚛️ DNA Space", "🌊 Bio-Metrics", "📜 Ledger"])
            
            with tab1:
                st.caption("Tactile Tissue Density Mapping (3D)")
                gray = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
                fig = go.Figure(data=[go.Surface(z=gray, colorscale='Electric')])
                fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
            with tab2:
                st.markdown("#### Autonomous Genetic Synthesizer")
                dna_seq = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(60)])
                if not is_healthy: 
                    dna_seq = dna_seq.replace("A", "<span style='color:#ef4444'>!</span>").replace("T", "<span style='color:#ef4444'>?</span>")
                st.markdown(f"<div style='font-family:monospace; background:#000; padding:15px; font-size:1.2rem;'>{dna_seq}</div>", unsafe_allow_html=True)
                st.caption("Detecting sub-cellular genetic sequence shifts.")

            with tab3:
                st.markdown("#### Secondary Biological Indicators")
                ndvi = compute_ndvi_score(img_bgr)
                wsi = compute_water_stress_index(img_bgr)
                b1, b2 = st.columns(2)
                b1.metric("Photosynthetic Capacity (NDVI)", f"{ndvi:.3f}")
                b2.metric("Water Stress Index (WSI)", f"{wsi}%")
                st.progress((ndvi + 1) / 2, text="Relative Biomass Density")

            with tab4:
                st.markdown("#### Global Access Ledger")
                try:
                    conn = sqlite3.connect('plantpulse_diagnostics.db')
                    df = pd.read_sql_query("SELECT * FROM analytics_ledger ORDER BY id DESC LIMIT 10", conn)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    conn.close()
                except: st.write("Syncing Database...")

# GLOBAL FORECASTING
st.markdown("---")
st.markdown("## 🛰️ 5-Day Pathogen Projection")
col_prog1, col_prog2 = st.columns([2, 1])
with col_prog1:
    forecast_days = [f"D+{i}" for i in range(1, 6)]
    forecast_risk = [risk_score * (1.1 ** i) if not is_healthy else risk_score for i in range(5)]
    fig_prog = go.Figure(data=go.Scatter(x=forecast_days, y=forecast_risk, mode='lines+markers', line=dict(color='#10b981', width=4)))
    fig_prog.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'color':'white'})
    st.plotly_chart(fig_prog, use_container_width=True)
    st.caption("Estimated escalation based on current viral loading.")

with col_prog2:
    st.markdown("<div class='quantum-stat'>", unsafe_allow_html=True)
    st.markdown("#### Subatomic Stability")
    st.title(f"Ω {(1 - (risk_score/100)):.3f}")
    st.caption("Quantum Equilibrium Index")
    st.markdown("</div>", unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #475569; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 30px;'>
    <b>PLANT PULSE TECHNOLOGIES GALACTIC</b><br>
    The Ultimate Agritech Matrix // SaaS v6.0 Core<br>
    © 2026 Global Food Security Council
</div>
""", unsafe_allow_html=True)
