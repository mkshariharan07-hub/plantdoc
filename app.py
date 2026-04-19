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
    page_title="PlantPulse SUPREME | Zenith v11.1",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# STYLE OVERRIDES (The SUPREME Highlight Aesthetic)
# ===============================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;800&family=Michroma&family=Space+Grotesk:wght@300;700&family=Outfit:wght@900&family=JetBrains+Mono&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

    .stApp {
        background: #010204 !important;
        background-image: 
            radial-gradient(circle at 10% 10%, rgba(34, 197, 94, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.1) 0%, transparent 40%),
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png') !important;
    }

    /* MASSIVE HIGHLIGHTS */
    .titan-name { 
        font-family: 'Syne', sans-serif; font-size: 6.5rem; font-weight: 800; 
        color: #ffffff; margin: 0; padding: 10px 40px; 
        background: linear-gradient(90deg, #064e3b, transparent);
        border-left: 10px solid #10b981;
        text-shadow: 0 0 30px rgba(16, 185, 129, 0.5);
        line-height: 1;
    }
    
    .status-badge-hero {
        font-family: 'Michroma', sans-serif; font-size: 2.2rem; font-weight: 800;
        padding: 15px 40px; border-radius: 20px; display: inline-block;
        margin-top: 20px; letter-spacing: 3px;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.3);
    }
    .status-healthy { background: #064e3b; color: #4ade80; border: 2px solid #10b981; }
    .status-infected { background: #450a0a; color: #f87171; border: 2px solid #ef4444; }

    .remedy-highlight {
        font-size: 1.6rem; color: #d1d5db; background: rgba(2, 44, 34, 0.8);
        padding: 35px; border-radius: 30px; border: 2px solid #10b981;
        box-shadow: inset 0 0 30px rgba(16, 185, 129, 0.1);
        line-height: 1.6; font-weight: 500;
    }

    /* ULTIMATE CARDS */
    .supreme-card {
        background: rgba(10, 10, 10, 0.9) !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        border-radius: 60px !important;
        padding: 65px;
        backdrop-filter: blur(60px);
        box-shadow: 0 100px 250px -50px rgba(0, 0, 0, 1);
        margin-bottom: 60px;
    }

    .kpi-main-big { font-family: 'JetBrains Mono', monospace; font-size: 4.5rem; color: #4ade80; font-weight: 800; }
</style>

<div id="leaves_supreme" class="leaf-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; overflow: hidden; display: none;">
    <div class="leaf" style="position: absolute; top: -100px; width: 50px; height: 50px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-supreme 5s linear infinite; left: 15%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 50px; height: 50px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-supreme 7s linear infinite; left: 45%;"></div>
    <div class="leaf" style="position: absolute; top: -100px; width: 50px; height: 50px; background: url('https://www.transparentpng.com/download/leaf/green-leaf-transparent-background-7.png') no-repeat; background-size: contain; animation: fall-supreme 4s linear infinite; left: 75%;"></div>
</div>
<style>
    @keyframes fall-supreme {
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
    st.markdown("<h2 style='text-align:center; color:#4ade80; font-family:Syne;'>PLANTEPULSE TITANIC</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🛠️ ZENITH CORE v11.1")
    st.markdown("""
    <div style='background: rgba(16, 185, 129, 0.05); border: 1px solid #10b981; border-radius: 12px; padding: 15px;'>
        <div style='margin-bottom:8px; font-family:Space Grotesk;'><span style='color:#1db954;'>●</span> PLANTNET NODE 24 [ACTIVE]</div>
        <div style='margin-bottom:8px; font-family:Space Grotesk;'><span style='color:#1db954;'>●</span> BIOSCAN ANALYTICS [SYNC]</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👑 CHIEF ARCHITECTS")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #020617, #064e3b); padding: 25px; border-radius: 20px; border: 1px solid #10b981; color: #fff;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>SINDHUJA R</b><br><small>226004099</small><hr style='margin:10px 0; opacity:0.1;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>SARASWATHY R</b><br><small>226004092</small><hr style='margin:12px 0; opacity:0.1;'>
        <b style='font-size:1.1rem; color:#4ade80; font-family:Syne;'>KIRUTHIKA U</b><br><small>226004052</small>
    </div>
    """, unsafe_allow_html=True)

# TICKER
st.markdown("""
<div style="background: #000; padding: 12px; border-radius: 12px; border: 1px solid #065f46; margin-bottom: 40px; box-shadow: 0 0 20px rgba(16,185,129,0.2);">
    <marquee scrollamount="6" style="color: #4ade80; font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight:800;">
        ⚡ ZENITH SYNC: 100% OPTIMAL &nbsp;&nbsp;█&nbsp;&nbsp; 💹 PREDICTED REVENUE: +$8.4B &nbsp;&nbsp;█&nbsp;&nbsp; 🧬 MOLECULAR STABILITY: 99.4% &nbsp;&nbsp;█&nbsp;&nbsp; 🛰️ ZENITH RADAR: ACTIVE &nbsp;&nbsp;█&nbsp;&nbsp;
    </marquee>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='font-family:Syne; font-size:6.5rem; text-align:center; color:#4ade80; letter-spacing:-5px; margin:0;'>ZENITH ANALYTICA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-family:Michroma; color:#10b981; letter-spacing:8px;'>ULTIMATE SUPREME PHYTOLOGY OVERDRIVE</p>", unsafe_allow_html=True)

# INGESTION
st.markdown("---")
c_i, c_p = st.columns([1,1], gap="large")

with c_i:
    st.markdown("### 📥 Neural Bio-Ingestion")
    mode = st.radio("Signal Path", ["Quantum Array", "Optical Path"], horizontal=True)
    img_bgr = None
    if mode == "Quantum Array":
        f = st.file_uploader("Select Multispectral Payload", type=["jpg","png","jpeg"])
        if f: img_bgr = decode_bytes_to_bgr(f.read())
    else:
        cam = st.camera_input("Active Specimen Zenith Scan")
        if cam: img_bgr = decode_bytes_to_bgr(cam.read())

with c_p:
    if img_bgr is not None:
        st.markdown("### 🔍 Specimen Zenith Matrix")
        st.markdown("""
        <div style='position:relative; width:100%; height:380px; border-radius:30px; overflow:hidden; border:2px solid #064e3b;'>
            <div style='position:absolute; width:100%; height:6px; background:#4ade80; box-shadow:0 0 20px #22c55e; animation:scan-ultimate 4s infinite;'></div>
            <img src='data:image/png;base64,""" + base64.b64encode(cv2.imencode('.png', img_bgr)[1]).decode() + """' style='width:100%; height:100%; object-fit:cover;'>
        </div>
        <style>@keyframes scan-ultimate { 0%, 100% { top: 0%; } 50% { top: 100%; } }</style>
        """, unsafe_allow_html=True)
    else:
        st.info("Awaiting specimen link for zenith terminal initialization...")

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
        variant = p_res.get('plant', 'Unknown')
        push(f"Class Refined: {variant}")
        
        c_res = identify_crop_health(img_bgr)
        pathogen = c_res.get('disease', 'Healthy')
        conf = c_res.get('confidence', 0)
        push(f"Pathogen Profile: {pathogen} ({conf}%)")
        
        push("Calibrating Aer-127 Quantum Backend...")
        qc, ent = build_quantum_circuit(img_bgr)
        counts, b_n = run_quantum(qc)
        risk_score, r_lvl = calculate_quantum_risk(counts, ent)
        
        push("Extracting Zenith Data...")
        n_v = compute_ndvi_score(img_bgr)
        nitro = estimate_nitrogen_content(img_bgr)
        rank = calculate_global_rank(nitro['nitrogen_pct'], n_v)
        
        is_h = "healthy" in pathogen.lower()
        if is_h:
            st.markdown("<script>document.getElementById('leaves_supreme').style.display = 'block'; setTimeout(() => { document.getElementById('leaves_supreme').style.display = 'none'; }, 7000);</script>", unsafe_allow_html=True)
        
        # RESULTS
        st.markdown("## 📊 Ultimate Analytical Command")
        d1, d2 = st.columns([1.2, 0.8], gap="large")
        
        with d1:
            st.markdown("<div class='supreme-card'>", unsafe_allow_html=True)
            # MASSIVE NAME & STATUS
            st.markdown(f"<div class='titan-name'>{variant.upper()}</div>", unsafe_allow_html=True)
            if is_h:
                st.markdown("<div class='status-badge-hero status-healthy'>🟢 SPECIMEN OPTIMAL</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='status-badge-hero status-infected'>🔴 CRITICAL: {pathogen.upper()}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"<div style='font-family:Michroma; color:#6e7681; font-size:0.8rem; letter-spacing:4px;'>ZENITH RANK</div><div class='kpi-main-big'>{rank['percentile']}%</div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div style='font-family:Michroma; color:#6e7681; font-size:0.8rem; letter-spacing:4px;'>QUANTUM RISK</div><div class='kpi-main-big' style='color:#f87171;'>{risk_score:.1f}%</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            # ACCURATE REMEDY
            oracle_info = get_disease_info(pathogen)
            remedy_text = oracle_info['tips']
            st.markdown(f"<p style='font-family:Michroma; font-size:1.1rem; color:#4ade80;'>🧬 TITANIC REMEDY PROTOCOL:</p>", unsafe_allow_html=True)
            st.markdown(f"<div class='remedy-highlight'>{remedy_text}</div>", unsafe_allow_html=True)
            
            if not is_h:
                links = get_remedy_purchase_links(pathogen)
                cols = st.columns(len(links) if links else 1)
                for i, l in enumerate(links):
                    with cols[i]:
                        st.markdown(f"<a href='{l['url']}' target='_blank' style='display:block; text-align:center; background:#4ade80; color:#010204; padding:18px; border-radius:24px; text-decoration:none; font-weight:900; font-size:1.1rem; box-shadow:0 10px 30px rgba(16,185,129,0.4);'>{l['icon']} {l['store'].upper()}</a>", unsafe_allow_html=True)
            
            st.markdown("---")
            pdf = generate_pdf_report(variant, pathogen, conf, r_lvl, "Treat now.", risk_score, 100-risk_score, {}, 0, {})
            st.download_button("📥 DOWNLOAD CLINICAL ZENITH REPORT", data=pdf, file_name=f"PlantPulse_Supreme_{variant}.pdf")
            st.markdown("</div>", unsafe_allow_html=True)

        with d2:
            st.markdown("<div class='supreme-card' style='padding:40px;'>", unsafe_allow_html=True)
            st.markdown("#### 🌀 Topological Bio-Mesh")
            res_gray = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY), (100, 100))
            fig = go.Figure(data=[go.Surface(z=res_gray, colorscale='Greens')])
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", scene_xaxis_visible=False, scene_yaxis_visible=False, scene_zaxis_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            st.markdown("#### ⚛️ Quantum Genetic Map")
            dna = "".join(["ATCG"[hash(variant+str(j)) % 4] for j in range(120)])
            st.markdown(f"<div style='font-family:JetBrains Mono; font-size:0.9rem; color:#10b981; word-break:break-all; background:#000; padding:15px; border-radius:12px; border:1px solid #064e3b;'>{dna}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ORACLE
st.markdown("---")
st.markdown("<h2 style='text-align:center; font-family:Syne; font-size:5rem; color:#4ade80; letter-spacing:-3px;'>🤖 THE ZENITH ORACLE</h2>", unsafe_allow_html=True)
q = st.text_input("Consult the Titanic Collective Intelligence...", placeholder="Ask the Oracle about growth, productivity, or specific symptoms...")
if q:
    ans = get_disease_info(q)
    st.markdown(f"""
    <div style="background:#0a0a0a; border:4px solid #4ade80; padding:60px; border-radius:50px; box-shadow: 0 0 120px rgba(34,197,94,0.4);">
        <h2 style='color:#4ade80; margin-top:0; font-family:Syne;'>Oracle Wisdom</h2>
        <p style='font-size:1.8rem; color:#d1d5db; line-height:1.7; font-family:Space Grotesk;'>{ans['tips']}</p>
        <div style='background:#064e3b; color:#4ade80; padding:15px 40px; border-radius:24px; font-weight:900; display:inline-block; font-size:1.8rem; font-family:Michroma; border:2px solid #10b981;'>SEVERITY: {ans['severity'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; color: #4ade80; opacity: 0.6; font-size: 1.1rem; padding-top: 60px; border-top: 2px solid #14532d; font-family:Space Grotesk;'>
    <b>PLANT PULSE TITANIC SUPREME v11.1</b><br>
    The Ultimate Genetic Intelligence Suite // Galactic Bio-Collective<br>
    © 2026 Sovereign Agritech Alliance
</div>
""", unsafe_allow_html=True)
