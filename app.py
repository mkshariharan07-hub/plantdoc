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
    predict_harvest_revenue, calculate_degrade_velocity
)

load_dotenv()

# ===============================
# PAGE CONFIGURATION
# ===============================
st.set_page_config(
    page_title="PlantPulse SUPREME | Zenith v12.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The TITANIC OVERDRIVE)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;800&family=Michroma&family=Space+Grotesk:wght@300;700&family=Outfit:wght@900&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #010204 !important;
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* SUPREME HIGHLIGHTS */
    .titan-name-v12 { 
        font-family: 'Syne', sans-serif; font-size: 5rem; font-weight: 800; 
        color: #fff; margin: 0; padding: 20px 40px; 
        background: linear-gradient(90deg, #064e3b, transparent);
        border-left: 15px solid #10b981;
        text-shadow: 0 0 30px rgba(16, 185, 129, 0.5);
    }
    
    .status-badge-v12 {
        font-family: 'Michroma', sans-serif; font-size: 1.8rem; font-weight: 800;
        padding: 20px 50px; border-radius: 30px; display: inline-block;
        margin-top: 25px; letter-spacing: 5px;
    }
    .status-v-opt { background: #064e3b; color: #4ade80; border: 3px solid #10b981; box-shadow: 0 0 50px rgba(34,197,94,0.3); }
    .status-v-crit { background: #450a0a; color: #f87171; border: 3px solid #ef4444; box-shadow: 0 0 50px rgba(239,68,68,0.3); }

    /* SEVERITY RADAR */
    .sev-box { padding: 30px; border-radius: 30px; border: 2px solid #30363d; background: rgba(0,0,0,0.5); text-align: center; }
    .sev-val { font-family: 'JetBrains Mono', monospace; font-size: 4rem; font-weight: 900; }
    
    /* REMEDY HIGHLIGHT */
    .remedy-titan {
        font-size: 1.5rem; color: #d1d5db; background: rgba(2, 44, 34, 0.85);
        padding: 40px; border-radius: 40px; border: 2px solid #10b981;
        box-shadow: inset 0 0 50px rgba(16, 185, 129, 0.2);
        line-height: 1.8;
    }

    /* SCANNERS */
    .scanner-line-v12 { position: absolute; width: 100%; height: 8px; background: #4ade80; box-shadow: 0 0 30px #22c55e; animation: scan-v12 3s infinite linear; }
    @keyframes scan-v12 { 0% { top: 0%; } 100% { top: 100%; } }
</style>

<div id="leaves_v12" class="leaf-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; display: none;">
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-v12 6s linear infinite; left: 20%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-v12 4s linear infinite; left: 50%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 60px; height: 60px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-v12 7s linear infinite; left: 80%;"></div>
</div>
<style>
    @keyframes fall-v12 {
        0% { transform: translateY(-100px) rotate(0deg); }
        100% { transform: translateY(110vh) rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# SIDEBAR
# ===============================
with st.sidebar:
    st.image("https://media1.tenor.com/m/Zf2qA9tOQ3QAAAAd/baby-groot.gif", use_container_width=True)
    st.markdown("<h2 style='text-align:center; color:#4ade80; font-family:Syne;'>ZENITH v12.0</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🛠️ ZENITH CORE OVERDRIVE")
    st.markdown("""
    <div style='background: rgba(16, 185, 129, 0.05); border: 1px solid #10b981; border-radius: 12px; padding: 15px;'>
        <div style='margin-bottom:8px;'><span style='color:#1db954;'>●</span> PLANTNET NODE 24 [ZENITH]</div>
        <div style='margin-bottom:8px;'><span style='color:#3b82f6;'>●</span> QUANTUM AER-127 [ZEN]</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👑 ZENITH ARCHITECTS")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #020617, #064e3b); padding: 20px; border-radius: 20px; border: 1px solid #10b981; color: #fff;'>
        <b style='color:#4ade80;'>SINDHUJA R</b> (226004099)<br>
        <b style='color:#4ade80;'>SARASWATHY R</b> (226004092)<br>
        <b style='color:#4ade80;'>KIRUTHIKA U</b> (226004052)
    </div>
    """, unsafe_allow_html=True)

# TICKER
st.markdown("""
<div style="background: #000; padding: 15px; border-radius: 20px; border: 1px solid #065f46; margin-bottom: 50px;">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight:800;">
        ⚡ ZENITH SYNC: 100% &nbsp;&nbsp;█&nbsp;&nbsp; 💹 SAVINGS REALIZED: +$8.4B &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 BIO-STABILITY: NOMINAL &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ RADAR: ACTIVE &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='font-family:Syne; font-size:7rem; text-align:center; color:#4ade80; line-height:1; letter-spacing:-6px;'>ZENITH OVERDRIVE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-family:Michroma; color:#10b981; letter-spacing:10px;'>SUPREME CLINICAL BIO-INTERFACE // v12.0</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
col_i, col_p = st.columns([1,1], gap="large")

with col_i:
    st.markdown("### 📥 Bio-Signature Ingestion")
    mode = st.radio("Protocol", ["Quantum Uplink", "Optical Path"], horizontal=True)
    img_bgr = None
    if mode == "Quantum Uplink":
        f = st.file_uploader("Select Multispectral Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Zenith Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with col_p:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Scanner Matrix")
        st.markdown("""
        <div style='position:relative; width:100%; height:400px; border-radius:40px; overflow:hidden; border:3px solid #064e3b;'>
            <div class='scanner-line-v12'></div>
            <img src='data:image/png;base64,""" + base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode() + """' style='width:100%; height:100%; object-fit:cover;'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen ingestion for terminal initialization...")

# OVERDRIVE EXECUTE
if img_bgr is not None:
    st.markdown("---")
    if st.button("🔥 INITIATE SUPREME ZENITH OVERDRIVE", use_container_width=True):
        
        # LOGS
        ph = st.empty()
        m = []
        def push(txt):
            m.append(f"<b>[SYSTEM]</b> {txt}")
            ph.markdown(f"<div style='font-family:JetBrains Mono; background:#000; padding:20px; border-radius:20px; border:1px solid #10b981; color:#34d399; height:120px; overflow-y:auto;'>{'<br>'.join(m)}</div>", unsafe_allow_html=True)
            time.sleep(0.2)

        push("Initializing Molecular Sync...")
        p_res = identify_plant_plantnet(img_bgr)
        c_res = identify_crop_health(img_bgr)
        
        variant = c_res.get('plant', 'Generic Specimen')
        pathogen = c_res.get('disease', 'Healthy Spectrum')
        conf = c_res.get('confidence', 0)
        sev_score = c_res.get('severity_score', 0)
        rec_prob = c_res.get('recovery_prob', 100)
        
        push(f"Class Identification: {variant}")
        push(f"Pathogen Profile: {pathogen} ({conf}%)")
        
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        is_h = "healthy" in pathogen.lower()
        if is_h:
            st.markdown("<script>document.getElementById('leaves_v12').style.display = 'block'; setTimeout(() => { document.getElementById('leaves_v12').style.display = 'none'; }, 8000);</script>", unsafe_allow_html=True)

        # RESULTS
        st.markdown("## 📊 Ultimate Analytical Command")
        d1, d2 = st.columns([1.2, 0.8], gap="large")
        
        with d1:
            st.markdown("<div class='supreme-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='titan-name-v12'>{variant.upper()}</div>", unsafe_allow_html=True)
            if is_h:
                st.markdown("<div class='status-badge-v12 status-v-opt'>🟢 BIO-SIGNATURE OPTIMAL</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='status-badge-v12 status-v-crit'>🔴 PATHOGEN: {pathogen.upper()}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            with k1: st.markdown(f"<div class='sev-box'><div style='color:#6e7681; font-family:Michroma; font-size:0.7rem;'>SEVERITY</div><div class='sev-val' style='color:#f87171;'>{sev_score}%</div></div>", unsafe_allow_html=True)
            with k2: st.markdown(f"<div class='sev-box'><div style='color:#6e7681; font-family:Michroma; font-size:0.7rem;'>RECOVERY</div><div class='sev-val' style='color:#4ade80;'>{rec_prob:.0f}%</div></div>", unsafe_allow_html=True)
            with k3: st.markdown(f"<div class='sev-box'><div style='color:#6e7681; font-family:Michroma; font-size:0.7rem;'>AI CONF</div><div class='sev-val'>{conf:.0f}%</div></div>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown(f"<div class='remedy-titan'><b>🧬 ZENITH REMEDY PROTOCOL:</b><br>{c_res.get('treatment', 'Maintain current regime.')}</div>", unsafe_allow_html=True)
            
            if not is_h:
                lks = get_remedy_purchase_links(pathogen)
                cols = st.columns(len(lks) if lks else 1)
                for i, l in enumerate(lks):
                    with cols[i]: st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; text-align:center; background:#4ade80; color:#010204; padding:20px; border-radius:24px; text-decoration:none; font-weight:900;'>{l['icon']} {l['store'].upper()}</a>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, r_lvl, "Treat now.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD CLINICAL ZENITH DOSSIER", data=pdf, file_name=f"PlantPulse_Zenith_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            st.markdown("<div class='supreme-card' style='padding:40px;'>", unsafe_allow_html=True)
            st.markdown("#### 🌀 Topological Bio-Mesh")
            fig = go.Figure(data=[go.Surface(z=cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100)), colorscale='Greens')])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            ndvi = compute_ndvi_score(img_bgr)
            st.metric("Photosynthetic Capacity (NDVI)", f"{ndvi:.4f}")
            st.progress((ndvi+1)/2, text="Leaf Vitality Saturation")
            st.markdown("</div>", unsafe_allow_html=True)

# DR LEAF
st.markdown("---")
st.markdown("<h2 style='text-align:center; font-family:Syne; font-size:4rem; color:#4ade80;'>🤖 THE ZENITH ORACLE v12.0</h2>", unsafe_allow_html=True)
q = st.text_input("Consult the Titanic Collective Intelligence...", placeholder="Ask about growth, productivity, or specific symptoms...")
if q:
    ans = get_disease_info(q)
    st.markdown(f"""
    <div style="background:#0a0a0a; border:4px solid #4ade80; padding:60px; border-radius:50px; box-shadow: 0 0 120px rgba(34,197,94,0.4);">
        <h2 style='color:#4ade80; margin-top:0;'>Oracle Wisdom</h2>
        <p style='font-size:1.6rem; color:#d1d5db; line-height:1.7; font-family:Space Grotesk;'>{ans['tips']}</p>
        <div style='background:#064e3b; color:#4ade80; padding:15px 40px; border-radius:24px; font-weight:900; display:inline-block;'>SEVERITY: {ans['severity'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 1.1rem; padding-top: 60px; border-top: 2px solid #14532d;'>
    <b>PLANT PULSE ZENITH SUPREME v12.0</b><br>
    The Ultimate High-Fidelity Suite // Galactic Bio-Collective<br>
    © 2026 Sovereign Agritech Alliance
</div>
""", unsafe_allow_html=True)
